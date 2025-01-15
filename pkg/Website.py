import json
import re

import unicodedata
from model.panGu import PanGuTable
from model.website import websiteTable
from pkg.db import Db
from tools.array import Array
from tools.file import File
from tools.sqlTool import SqlTool
from tools.threadingTool import MyThreading


class Website:
    def __init__(self, param=None, param2=None, path=None):
        self.param = param
        self.param2 = param2
        self.path = path
        self.resData = []
        self.resData2 = []
        self.resData3 = []
        self.map = {}
        self.target = []

    def colorTranslate(self):
        translateMap = {}
        sql = websiteTable(index="getTmpColor").getSql()
        data = Db(sql=sql, param=(), db="panGuWebPron").getAll()
        for i in data:
            tmpKey = "{}-{}".format(i.get("color").lower(), i.get("languages_id"))
            translateMap[tmpKey] = i.get("value").lower()

        self.fixAttribute(translateMap)
        self.fixStyle(translateMap)

        File(path="../.././data/websiteUpdateColorTranslateSql.txt", txtData=self.resData).writeTxt()
        File(path="../.././data/websiteGuBackupColorTranslateSql.txt", txtData=self.resData2).writeTxt()

    def fixAttribute(self, translateMap):
        print("website attribute language")
        sql = websiteTable(index="getAttributeDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="websiteTest").getAll()

        for i in data:
            tmpKey = "{}-{}".format(i.get("color").lower(), i.get("languages_id"))
            if translateMap.get(tmpKey) is not None:
                if self.remove_accents(translateMap.get(tmpKey)) != self.remove_accents(i.get("value").lower()):
                    self.resData.append(
                        '''update jjshouse.attribute_languages_v2 set attr_values = "{}" where attr_lang_id = {};'''.format(
                            translateMap.get(tmpKey).rstrip(), i.get("attr_lang_id")))
                    self.resData2.append(
                        '''update jjshouse.attribute_languages_v2 set attr_values = "{}" where attr_lang_id = {};'''.format(
                            i.get("value"), i.get("attr_lang_id")))

    def fixStyle(self, translateMap):
        print("website style language")
        sql = websiteTable(index="getStyleDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="websiteTest").getAll()

        for i in data:
            tmpKey = "{}-{}".format(i.get("color").lower(), i.get("languages_id"))
            if translateMap.get(tmpKey) is not None:
                if self.remove_accents(translateMap.get(tmpKey)) != self.remove_accents(i.get("value").lower()):
                    self.resData.append(
                        '''update jjshouse.style_languages set `value` = "{}" where sl_id = {};'''.format(
                            translateMap.get(tmpKey).rstrip(), i.get("sl_id")))
                    self.resData2.append(
                        '''update jjshouse.style_languages set `value` = "{}" where sl_id = {};'''.format(
                            i.get("value"), i.get("sl_id")))

    @staticmethod
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def sizeAndColorSort(self):
        for c in self.param:
            print("开始处理品类：{} 数据".format(c))
            goodsStyleInfo = {}
            # 获取当前品类下的商品id
            sql = websiteTable(index="getGoodsIdByCategoryId").getSql()
            data = Db(sql=sql, param=c, db="websitePron", ).getAll()

            for s in data:
                pattern1 = re.compile(r'^(xxs|xs|s|m|l|xl|xxl|3xl|4xl|5xl|6xl|7xl|8xl|free size)$',
                                      re.IGNORECASE)  # 匹配 xxs, xs, s, m, l, xl, xxl 模式（不区分大小写）
                pattern2 = re.compile(r'^(\d+)#$', re.IGNORECASE)  # 匹配 1#, 2#, 3#... 模式（这里不需要区分大小写，但包含以防万一）

                pattern3 = re.compile(r'^\d+$')

                # 检查字符串是否符合其中一个模式
                if pattern1.match(s.get("value")) or pattern2.match(s.get("value")) or pattern3.match(
                        s.get("value")):

                    if s.get("name").lower() == 'size':
                        if goodsStyleInfo.get(s.get("cat_id")) is None:
                            goodsStyleInfo[s.get("cat_id")] = {"size": [s]}
                        else:
                            if goodsStyleInfo[s.get("cat_id")].get("size") is None:
                                goodsStyleInfo[s.get("cat_id")]['size'] = [s]
                            else:
                                goodsStyleInfo[s.get("cat_id")].get("size").append(s)
                    else:
                        if goodsStyleInfo.get(s.get("cat_id")) is None:
                            goodsStyleInfo[s.get("cat_id")] = {"color": [s]}
                        else:
                            if goodsStyleInfo[s.get("cat_id")].get("color") is None:
                                goodsStyleInfo[s.get("cat_id")]['color'] = [s]
                            else:
                                goodsStyleInfo[s.get("cat_id")].get("color").append(s)

            self.map = self.map | goodsStyleInfo

        for k, v in self.map.items():
            newData = self.sortData(v)

            for s, m in newData.items():
                newList = [d['display_order'] for d in m]
                oldSortData = sorted(newList, key=lambda x: int(x))
                newSortData = self.fixSortData(m)
                tmpList = self.sortByList(m, newSortData)
                print(oldSortData, newSortData, tmpList)
                flag = False
                if 0 in oldSortData:
                    flag = True
                for x, y in enumerate(tmpList):
                    print(x)
                    if x + 1 == oldSortData[x] and flag is False:
                        continue

                    tmpId = y.get("style_id")
                    tmpOrder = y.get("display_order")
                    if flag is True or tmpOrder == 0:
                        tmpOrder = x + 1

                    if y.get("display_order") == oldSortData[x] and y.get("display_order") != 0 and flag is False:
                        continue
                    if tmpOrder != oldSortData[x]:
                        tmpOrder = oldSortData[x]
                    self.resData.append(
                        SqlTool(data=y, table="style", condition="style_id").createUpdateStatements())
                    self.resData2.append(
                        "UPDATE style SET display_order = %s WHERE style_id = %s;" % (
                            tmpOrder, tmpId))

        print("开始写入备份数据")
        File(path="../.././data/fixStyleBak.txt", txtData=self.resData).writeTxt()
        print("开始写入更新数据")
        File(path="../.././data/fixStyleUpdate.txt", txtData=self.resData2).writeTxt()

    @staticmethod
    def sortData(data):
        backInfo = {}
        if data.get("size") is not None:
            backInfo['size'] = sorted(data.get("size"), key=lambda x: x['display_order'])
        if data.get("color") is not None:
            backInfo['color'] = sorted(data.get("color"), key=lambda x: x['display_order'])

        return backInfo

    def fixSortData(self, data):
        tmpList = []
        newList = [d['value'] for d in data]

        if self.withSpecialChart(newList) is True:
            tmpList = sorted(newList, key=lambda x: int(x[:-1]))
        if self.withNumberChart(newList) is True:
            tmpList = sorted(newList, key=lambda x: int(x))
        if self.withSizeChart(newList) is True:
            tmpList = self.customSortSizes(newList)
        return tmpList

    @staticmethod
    def withSpecialChart(lst):
        pattern = r'^\d+#$'
        return all(re.match(pattern, item) is not None for item in lst)

    @staticmethod
    def withNumberChart(lst):
        for item in lst:
            if not isinstance(item, (int, float)):
                return False
        return True

    @staticmethod
    def withSizeChart(lst):
        pattern1 = r'^(?:2[89]|3[0-6]|XXS|3XL|4XL|5XL|6XL|7XL|8XL|XS|S|M|L|XL|[1-9]|1[0-2]|Free Size)$'
        pattern2 = r'^(?:XS|S|M|L|XL|XXL|[3-6]XL|Free Size)$'

        if all(re.match(pattern1, item) is not None for item in lst):
            return True
        elif all(re.match(pattern2, item) is not None for item in lst):
            return True
        else:
            return False

    @staticmethod
    def customSortSizes(sizes):
        # 定义一个字典来映射每个尺寸到它的排序权重
        size_order = {
            '5': 1, '6': 2, '7': 3, '8': 4, '9': 5, '10': 6, '11': 7, '12': 8, '28': 9, '29': 10, '30': 11, '31': 12,
            '32': 13, '33': 14, '34': 15, '35': 16, '36': 17,
            'XXS': 18, 'XS': 19, 'S': 20, 'M': 21, 'L': 22,
            'XL': 23, 'XXL': 24, '3XL': 25, '4XL': 26, '5XL': 27,
            '6XL': 28, '7XL': 29, '8XL': 30, 'Free Size': 31
        }

        # 使用 sorted() 函数和自定义的排序键来排序列表
        sorted_sizes = sorted(sizes, key=lambda size: size_order[size])

        return sorted_sizes

    @staticmethod
    def get_order_index(data, order_list):
        value = data['value']
        try:
            return order_list.index(value)
        except ValueError:
            return len(order_list)

    def sortByList(self, data, order):
        return sorted(data, key=lambda tmpData: self.get_order_index(tmpData, order))

    def getStockDiff(self):
        # 获取网站库存数据
        sql = websiteTable(index="getWebStockData").getSql()
        data = Db(sql=sql, param=self.param, db="websitePron").getAll()

        webStockMap = {}
        skuList = []
        for i in data:
            webStockMap[i.get("psku")] = i.get("stock")
            skuList.append(i.get("psku"))

        pSkuList = Array(target=skuList, step=500).ArrayChunk()

        panGuStockMap = {}

        for m in pSkuList:
            # 获取库存服务数据
            sql = PanGuTable(index="getPanguStockData").getSql()
            data = Db(sql=sql, param="','".join(m), db="panguStockDb").getAll()
            for s in data:
                panGuStockMap[s.get("sku")] = {"a": s.get("available_num"), "b": s.get("available_tryon_num")}

        diffSku = {}
        diffList = []
        for k, v in webStockMap.items():
            if k not in panGuStockMap:
                # diffSku[k] = {"web": v, "pangu": '无'}
                continue

            if v != panGuStockMap[k].get('a') and v != panGuStockMap[k].get('b'):
                diffSku[k] = {"web": v, "all": panGuStockMap[k].get('a'), "tryon": panGuStockMap[k].get('b')}

        print("差异数量：", len(diffSku))

        for k, v in diffSku.items():
            diffList.append(k)
            print(k, v)

        File(path="../.././data/diffStock.txt", txtData=diffList).writeTxt()

    def getPlusDeleteData(self):

        sql = websiteTable(index="getGoodsPlusData").getSql()
        data = Db(sql=sql, param="','".join(self.param), db="websitePron").getAll()

        newList = Array(target=data, step=100).ArrayChunk()

        MyThreading(num=20, data=newList, func=self.getFixPlusImgData).semaphoreJob()

        print(self.resData)

    def getFixPlusImgData(self, data, desc, semaphore):
        print("开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        for i in data:
            goodsId = i.get('goods_id')
            print("开始处理 {}".format(goodsId))
            if i.get('ext_name') == 'rear_image_plus_json':
                tmpList = list(json.loads(i.get('ext_value')).values())
                sql = websiteTable(index="getGoodsShopByColorImg").getSql()
                tmpData = Db(sql=sql, param=(goodsId, "','".join(tmpList)), db="websitePron").getOne()
                if tmpData is not None:
                    self.resData.append(goodsId)
            else:
                sql = websiteTable(index="getGoodsPhotoImg").getSql()
                tmpData = Db(sql=sql, param=i.get('ext_value'), db="websitePron").getOne()
                if tmpData is not None:
                    self.resData.append(goodsId)
        # 释放锁
        semaphore.release()

    def getCombineProductSql(self):
        sql = websiteTable(index="getCombineProductSql").getSql()
        data = Db(sql=sql, param=(), db="websitePron").getAll()
        mappingMap = {}

        for i in data:
            if mappingMap.get(i.get('ext_value')) is not None:
                mappingMap.get(i.get('ext_value')).append(i.get('goods_id'))
            else:
                mappingMap[i.get('ext_value')] = [i.get('goods_id')]
        sqlList = []
        for k, v in mappingMap.items():
            sql = websiteTable(index="getCombineGoods").getSql()
            data = Db(sql=sql, param=k, db="websitePron").getOne()

            sql = websiteTable(index="getCombineTpl").getSql()
            tplData = Db(sql=sql, param=data.get("tpl_id"), db="websitePron").getOne()

            mapping = json.loads(data.get("mapping"))
            tmpMapping = {v: k for k, v in mapping.items()}
            for m in v:
                sql = "insert into pangu_website.combination_mapping(cp_id, cat_id, goods_id, attr_id, create_time) values(%s, %s, %s, %s, '%s');" % (k, tplData.get("cat_id"), m, tmpMapping.get(m), '2025-01-06 14:00:00')
                sqlList.append(sql)

        File(path="../.././data/combineGoodsMap.txt", txtData=sqlList).writeTxt()

    def asyncBuyTheLook(self):
        sql = websiteTable(index="getBuyTheLookData").getSql()
        data = Db(sql=sql, param=(), db="websitePron").getAll()
        for i in data:
            delete = 0
            if i.get("is_display") == 0:
                delete = 1
            insertSql1 = "INSERT INTO pangu_website.buy_the_look_config(cat_id, goods_id, gallery_id, is_delete, created_at) VALUES ({}, {}, 0, {}, '{}');"\
                .format(i.get("cat_id"), i.get("goods_id"), delete, i.get("last_update_time"))

            btlId = Db(sql=insertSql1, param=(), db="panGuWeb", showlog=True).execute()
            num = 1
            info = json.loads(i.get("ext_value"))

            for k, v in info.get("related_goods").items():

                insertSql2 = "INSERT INTO pangu_website.buy_the_look_product(btl_id, goods_id, `value`, `index`, is_delete, created_at) VALUES ({}, {}, '{}', {}, {}, '{}');"\
                .format(btlId, k, v, num, delete, i.get("last_update_time"))
                num = num + 1
                Db(sql=insertSql2, param=(), db="panGuWeb", showlog=True).execute()
