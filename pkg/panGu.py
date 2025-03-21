import json
import os
import time
from pathlib import Path

import openpyxl
import requests
from model.panGu import PanGuTable
from model.website import websiteTable
from pkg.db import Db
from tools.array import Array
from tools.curl import Curl
from tools.file import File
from tools.show import Show
from tools.sqlTool import SqlTool
from tools.threadingTool import MyThreading


class PanGu:
    def __init__(self, param=None, param2=None, parma3=None, path=None, limit=None, offset=None):
        self.param = param
        self.param2 = param2
        self.param3 = parma3
        self.path = path
        self.resData = []
        self.resData2 = []
        self.resMap = {}
        self.limit = limit
        self.offset = offset

    def pskuCloneMapping(self):
        startTime = time.time()
        # 获取映射关系
        sql = PanGuTable(index="getCloneData").getSql()
        cloneData = Db(sql=sql, param=(), db="panGuDb").getAll()
        # 将数据分组处理
        tmpList = Array(target=cloneData, step=1000).ArrayChunk()
        # 开启多线程消费数据
        MyThreading(num=10, data=tmpList, func=self.getSkuInfo).semaphoreJob()
        print("多线程结束 , 获取映射数据 {} 条".format(len(self.resData)))
        # 写入excel
        File(path=self.path, fileData={0: self.resData}, sheetName={0: "psku映射关系表"},
             sheetTitle={0: ["origin_psku", "clone_psku"]}).writeExcel()
        endTime = time.time()
        print("文件保存成功！本次服务耗时：{}".format(endTime - startTime))

    def getSkuInfo(self, data, desc, semaphore):
        # 上锁
        semaphore.acquire()
        if len(data) > 0:
            print("开始处理 {} 数据".format(desc))
            originSkuId = [str(m.get('origin_sku_id')) for m in data]
            cloneSkuId = [str(m.get('cloned_sku_id')) for m in data]
            tmpIdList = originSkuId + cloneSkuId
            # 获取sku数据
            sql = PanGuTable(index="getSkuInfo").getSql()
            skuInfo = Db(sql=sql, param=(",".join(tmpIdList)), db="panGuDb").getAll()
            reflectMap = {}
            for h in skuInfo:
                reflectMap[h.get('id')] = h.get('sku')
            for m in data:
                self.resData.append({"origin_psku": reflectMap.get(m.get("origin_sku_id")),
                                     "clone_psku": reflectMap.get(m.get("cloned_sku_id"))})
        # 释放锁
        semaphore.release()

    def getStockSkuInfo(self):
        plist = []
        page = 0
        while True:
            offset = page * self.limit
            print("开始获取：{}--{}".format(offset, offset + self.limit))
            sql = PanGuTable(index="getStockSku").getSql()
            stockData = Db(sql=sql, param=(self.param, self.param2, self.limit, offset), db="panguStockDb",
                           showlog=True).getAll()

            if len(stockData) == 0:
                break
            else:
                page = page + 1

            for i in stockData:
                plist.append(i.get("sku", ""))

        self.param = plist
        tmpList = Array(target=self.param, step=10000).ArrayChunk()

        # 开启多线程消费数据
        MyThreading(num=2, data=tmpList, func=self.syncStockData).semaphoreJob()

    def getColorImgDefaultData(self):

        # 获取当前有多少满足条件的商品
        sql = PanGuTable(index="getGoodsColorGoodsId").getSql()
        data = Db(sql=sql, param=self.param, db="panGuWeb").getAll()

        goodsList = []

        for i in data:
            goodsList.append(str(i.get('id')))

        print("开始计算本次一共需要拉取的商品数据量：{}".format(len(goodsList)))

        if len(goodsList) == 0:
            print("暂无需要执行的数据.. See you next time")

        # 将商品分组
        tmpList = Array(target=goodsList, step=1000).ArrayChunk()

        print("开启多线程拉取颜色图数据")
        # 开启多线程消费数据
        MyThreading(num=5, data=tmpList, func=self.getGoodsColorImgData).semaphoreJob()

        print("总共待处理商品数：{}".format(len(self.resMap)))

        goodsColorList = list(self.resMap.values())

        tmpList = Array(target=goodsColorList, step=500).ArrayChunk()
        print(tmpList)
        print("开启多线程处理颜色图数据")
        # 开启多线程消费数据
        MyThreading(num=20, data=tmpList, func=self.dealGoodsColorImgData).semaphoreJob()

        excelMap = {}

        for i in self.resData:
            if excelMap.get(i.get('cat_id')) is not None:
                excelMap[i.get('cat_id')].append(i)
            else:
                excelMap[i.get('cat_id')] = [i]

        categoryList = list(excelMap.keys())
        categoryData = {}
        categoryName = {}
        categoryTitle = {}
        num = 0
        for m in categoryList:
            categoryData[num] = excelMap.get(m)
            categoryName[num] = "C" + str(m)
            categoryTitle[num] = ["goods_id", "color", "is_default", "url", "type", "image_id"]
            num = num + 1
        print(categoryData)
        exit()
        # 写入excel
        File(path=self.path, fileData=categoryData, sheetName=categoryName,
             sheetTitle=categoryTitle).writeExcel()

        # tmpList = Array(target=list(categoryName.values()), step=1).ArrayChunk()
        # tmpList = [['C7'], ['C288']]
        # for i in tmpList:
        #     self.translateImg(i[0])
        # 开启多线程消费数据
        # MyThreading(num=40, data=tmpList, func=self.translateImg).semaphoreJob()

        print("数据处理结束！")

    def syncStockData(self, data, desc, semaphore):
        # 上锁
        semaphore.acquire()

        config = File(path="\config\config.json").read_json_config()
        url = "{}/v1/stocks/sync-from-erp".format(config["panGuUrl"]["stockUrl"])

        tmpList = Array(target=data, step=1000).ArrayChunk()
        num = 1
        for i in tmpList:
            print("开始处理 {} 数据 第{}批次开始".format(desc, num))
            Curl(url=url, param=json.dumps({"skus": i})).syncStockInfo()
            print("开始处理 {} 数据 第{}批次结束".format(desc, num))
            num = num + 1
        # 释放锁
        semaphore.release()

    def getGoodsColorImgData(self, data, desc, semaphore):
        # 上锁
        semaphore.acquire()

        tmpList = Array(target=data, step=100).ArrayChunk()
        num = 1
        for i in tmpList:
            print("开始拉取 {} 数据 第{}批次开始".format(desc, num))
            sql = PanGuTable(index="getGoodsColorInfo").getSql()
            data = Db(sql=sql, param=(",".join(i), self.param), db="panGuWeb").getAll()
            for m in data:
                if self.resMap.get(m.get("goods_id")) is None:
                    self.resMap[m.get("goods_id")] = [m]
                else:
                    self.resMap[m.get("goods_id")].append(m)

            print("开始拉取 {} 数据 第{}批次结束".format(desc, num))
            num = num + 1
        # 释放锁
        semaphore.release()

    def dealGoodsColorImgData(self, data, desc, semaphore):
        # 上锁
        semaphore.acquire()

        num = 1
        for i in data:
            print("开始处理 {} 数据 第{}批次开始".format(desc, num))
            tmpMap = {}
            for m in i:
                color = m.get('img_color', "")
                if color != '':
                    if tmpMap.get(color) is not None:
                        tmpMap[color].append(m)
                    else:
                        tmpMap[color] = [m]

            # 检查汇总后的颜色是否缺少设置默认色
            for key, value in tmpMap.items():
                status = False
                tmpLists = []

                for s in value:
                    if s.get('is_default', 0) == 1:
                        status = True
                    tmpLists.append(s)

                if status:
                    continue
                else:
                    self.resData.extend(tmpLists)
            print("开始处理 {} 数据 第{}批次结束".format(desc, num))
            num = num + 1
        # 释放锁
        semaphore.release()

    def translateImg(self, data):

        print("开始处理 数据开始 品类 {}".format(data))
        File(path=self.path, sheetName=data, index="D", target="G").urlToImg()
        print("开始处理 数据结束 品类 {}".format(data))

    def getHistoryData(self):
        sql = "select * from goods_gallery where goods_id in (%s) and img_type = '%s' and is_delete = 0"
        data = Db(sql=sql, param=(",".join(map(str, self.param2)), self.param), db="websiteTest").getAll()

        for m in data:
            if self.resMap.get(m.get("goods_id")) is None:
                self.resMap[m.get("goods_id")] = [m]
            else:
                self.resMap[m.get("goods_id")].append(m)

        goodsColorList = list(self.resMap.values())

        tmpList = Array(target=goodsColorList, step=500).ArrayChunk()

        print("开启多线程处理颜色图数据")
        # 开启多线程消费数据
        MyThreading(num=20, data=tmpList, func=self.dealGoodsColorImgData).semaphoreJob()

        File(path=self.path, fileData={0: self.resData}, sheetName={0: '426'},
             sheetTitle={0: ["goods_id", "img_color", "is_default", "img_url", "img_type", "img_id"]}).writeExcel()

    def fixHistoryColorImageData(self):
        updateList = []
        updateMap = {}
        for i in self.param:
            Show(text="创建入库单：", style="red").print()
            backUpList = []
            # 读取excel 中数据
            excelData = File(path=self.path, sheetName=i).readExcelSheet()
            if len(excelData) == 0:
                continue
            else:
                # 找出需要处理的图片
                for s in excelData:
                    updateMap[s.get("goods_id")] = s.get("goods_id")
            #             if s.get("is_default") == 1:
            #                 # 获取当前图片image_id
            #                 sql = PanGuTable(index="getGoodsImageInfo").getSql()
            #                 data = Db(sql=sql, param=(s.get("goods_id"), s.get("url").replace("https://cdn-4.jjshouse.com"
            #                                                                                   "/upimg/l/", "")),
            #                           db="panGuWebPron").getOne()
            #                 if len(data) == 0:
            #                     continue
            #                 insertSql = SqlTool(table="pangu_website.goods_gallery_v2", data=data).createInsertStatements()
            #
            #                 backUpList.append(insertSql)
            #                 updateList.append("UPDATE pangu_website.goods_gallery_v2 SET is_default = 1 WHERE id = {};".format(data.get('id')))
            #                 updateMap[data.get("goods_id")] = data.get("goods_id")
            #     if len(backUpList) > 0:
            #
            #         File(path="../.././data/{}bk.txt".format(i), txtData=backUpList).writeTxt()
            # if len(updateList) > 0:
            #     File(path="../.././data/shopbycolor.txt", txtData=updateList).writeTxt()
            #
            # print(len(updateMap))
            # print(list(updateMap.values()))
            print(len(list(updateMap.values())))
            aa = list(updateMap.values())
            print(",".join(map(str, aa)))

    def getInsertCategoryData(self):
        category = [8, 9, 10, 16, 17, 18, 22, 45]
        tryOnAndSamples = ['400', '420']
        attribute = ['Ruby Rose Garden', 'Sapphire Blooms', 'Sage Green Garden', 'Blush Rose Blooms', 'Azure Floral']

        # 获取样衣试衣对应的shop by color 属性id
        sql = PanGuTable(index="tryOnAndSamples").getSql()
        data = Db(sql=sql, param=",".join(tryOnAndSamples), db="panGuWebPron").getAll()
        for i in data:
            category.append(i.get("id"))

        attributeId = []
        # 获取属性id
        sql = PanGuTable(index="getAttrByValue").getSql()
        data = Db(sql=sql, param="','".join(attribute), db="panGuWebPron").getAll()
        for i in data:
            attributeId.append(i.get("id"))

        updateSql = []
        # 组装sql
        for n in category:
            # 获取当前品类最大排序值
            sql = PanGuTable(index="getCategoryAttributeMaxSort").getSql()
            data = Db(sql=sql, param=n, db="panGuWebPron").getOne()
            order = data.get("order") + 1
            for m in attributeId:
                tmpSql = '''INSERT INTO `pangu_website`.`category_attribute` (cat_id, attr_id, is_delete, updated_at, display_order, is_necessary, display_filter) VALUES ({}, {}, 0, NOW(), {}, 0, -1);'''.format(
                    n, m, order)
                updateSql.append(tmpSql)
                order += 1

        File(path=self.path, txtData=updateSql).writeTxt()

    def moveAttributeData(self):
        print("copy attribute data")
        print("copy pangu attribute")
        panGuIdList = self.copyPanGuAttr()
        print("copy pangu attributeLanguage")
        self.copyPanGuAttrLang(panGuIdList)
        print("copy pangu categoryAttribute")
        self.copyPanGuCategoryAttr(panGuIdList)
        print("copy pangu web attribute")
        panGuWebList = self.copyPanWebAttr()
        print("copy pangu web attributeLanguage")
        self.copyPanWebAttrLang(panGuWebList)
        print("copy pangu web categoryAttribute")
        self.copyPanWebCategoryAttr(panGuWebList)

    def moveStyleData(self):
        print("copy style data")
        print("copy pangu style")
        panGuIdList = self.copyPanGuStyle()
        print("copy pangu style language")
        self.copyPanGuStyleLang(panGuIdList)
        print("copy pangu category style")
        self.copyPanguCategoryStyle(panGuIdList)
        print("copy pangu web style")
        panGuWebList = self.copyPanWebStyle()
        print("copy pangu web style language")
        self.copyPanWebStyleLang(panGuWebList)

    def copyPanGuAttr(self):
        idList = []
        sql = PanGuTable(index="copyPanguAttributeData").getSql()
        data = Db(sql=sql, param=("','".join(self.param2), self.param3), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu.attribute", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu.attribute").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()
            idList.append(str(i.get("id")))
        return idList

    def copyPanGuAttrLang(self, idList):
        if idList is None or len(idList) == 0:
            return
        color = self.param2
        sql = PanGuTable(index="copyPanguAttributeLanguageData").getSql()
        data = Db(sql=sql, param=(",".join(idList)), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu.attribute_languages", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu.attribute_languages").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    def copyPanGuCategoryAttr(self, idList):
        if idList is None or len(idList) == 0:
            return
        catId = self.param
        sql = PanGuTable(index="copyPanguCategoryAttributeData").getSql()
        data = Db(sql=sql, param=(",".join(idList)), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu.category_attribute", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu.category_attribute").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    def copyPanWebAttr(self):
        idList = []
        sql = PanGuTable(index="copyPanguWebAttributeData").getSql()
        data = Db(sql=sql, param=("','".join(self.param2), self.param3), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu_website.attribute", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu_website.attribute").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()
            idList.append(str(i.get("id")))
        return idList

    def copyPanWebAttrLang(self, idList):
        if idList is None or len(idList) == 0:
            return
        color = self.param2
        sql = PanGuTable(index="copyPanguWebAttributeLanguageData").getSql()
        data = Db(sql=sql, param=(",".join(idList)), db="panGuWebPron").getAll()
        if data is None:
            return
        for i in data:
            self.checkExistAndClean("pangu_website.attribute_languages_v2",
                                    "attr_lang_id = {}".format(i.get("attr_lang_id")))
            sqlList = SqlTool(data=i, table="pangu_website.attribute_languages_v2").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    def copyPanWebCategoryAttr(self, idList):
        if idList is None or len(idList) == 0:
            return
        catId = self.param
        sql = PanGuTable(index="copyPanguWebCategoryAttributeData").getSql()
        data = Db(sql=sql, param=(",".join(idList), catId), db="panGuWebPron").getAll()
        if data is None:
            return
        for i in data:
            self.checkExistAndClean("pangu_website.category_attribute", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu_website.category_attribute").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    def copyPanGuStyle(self):
        idList = []
        sql = PanGuTable(index="copyPanguStyleData").getSql()
        data = Db(sql=sql, param=("','".join(self.param2), self.param3), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu.style", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu.style").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()
            idList.append(str(i.get("id")))
        return idList

    def copyPanGuStyleLang(self, idList):
        if idList is None or len(idList) == 0:
            return
        color = self.param2
        sql = PanGuTable(index="copyPanguStyleLanguageData").getSql()
        data = Db(sql=sql, param=(",".join(idList)), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu.style_languages",
                                    "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu.style_languages").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    def copyPanguCategoryStyle(self, idList):
        if idList is None or len(idList) == 0:
            return
        catId = self.param
        sql = PanGuTable(index="copyPanguCategoryStyleData").getSql()
        data = Db(sql=sql, param=(",".join(idList)), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu.category_style", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu.category_style").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    def copyPanWebStyle(self):
        idList = []
        sql = PanGuTable(index="copyPanWebStyleData").getSql()
        data = Db(sql=sql, param=("','".join(self.param2), self.param3), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu_website.style", "id = {}".format(i.get("id")))
            sqlList = SqlTool(data=i, table="pangu_website.style").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()
            idList.append(str(i.get("id")))
        return idList

    def copyPanWebStyleLang(self, idList):
        if idList is None or len(idList) == 0:
            return
        color = self.param2
        sql = PanGuTable(index="copyPanWebStyleLanguageData").getSql()
        data = Db(sql=sql, param=(",".join(idList)), db="panGuWebPron").getAll()
        if data is None or len(data) == 0:
            return
        for i in data:
            self.checkExistAndClean("pangu_website.style_languages",
                                    "sl_id = {}".format(i.get("sl_id")))
            sqlList = SqlTool(data=i, table="pangu_website.style_languages").createInsertStatements()
            Db(sql=sqlList, param=(), db="panGuWeb").execute()

    @staticmethod
    def checkExistAndClean(table, condition):
        sql = "select * from {} where {}".format(table, condition)
        # 检查表中是否存冲突数据
        data = Db(sql=sql, param=(), db="panGuWeb").getOne()
        if data is not None:
            # 删除冲突数据
            Db(sql="delete from {} where {}".format(table, condition), param=(), db="panGuWeb").execute()

    def getColorData(self):
        data = File(path=self.param).read_excl()
        saveDate = []

        sql = websiteTable(index="getTmpColor").getSql()
        existData = Db(sql=sql, param=(), db="panGuWebPron").getAll()
        existMap = {}
        for i in existData:
            existMap[i.get("color") + "-" + str(i.get("languages_id"))] = i.get("value")

        for i in data:
            if len(i) != len(self.param2) + 1:
                print("数据格式错误")
                continue
            num = 1
            for m in self.param2:

                sql = '''insert into pangu_website.tmp_color(color, languages_id, value) VALUES("{}", {}, "{}")'''.format(
                    i[0], m, i[num]);

                if existMap.get(i[0] + "-" + str(m)) != i[num]:
                    print(sql)
                saveDate.append(sql)
                num = num + 1
        # for s in saveDate:
        #     Db(sql=s, param=(), db="panGuWeb").execute()

    def colorTranslate(self):

        self.fixWebAttribute()
        self.fixWebStyle()
        self.fixPanAttribute()
        self.fixPanStyle()

        File(path="../.././data/panGuUpdateColorTranslateSql.txt", txtData=self.resData).writeTxt()
        File(path="../.././data/panGuBackupColorTranslateSql.txt", txtData=self.resData2).writeTxt()

    def fixWebAttribute(self):
        print("pangu website attribute language")
        sql = PanGuTable(index="getWebAttributeDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="panGuWebPron",
                  ).getAll()

        if len(data) > 0:
            for i in data:
                self.resData.append(
                    '''update pangu_website.attribute_languages_v2 set attr_values = "{}" where attr_lang_id = {};'''.format(
                        i.get("tmp_value").rstrip(), i.get("attr_lang_id")))
                self.resData2.append(
                    '''update pangu_website.attribute_languages_v2 set attr_values = "{}" where attr_lang_id = {};'''.format(
                        i.get("attr_values"), i.get("attr_lang_id")))

    def fixWebStyle(self):
        print("pangu website style language")
        sql = PanGuTable(index="getWebStyleDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="panGuWebPron",
                  ).getAll()
        if len(data) > 0:
            for i in data:
                self.resData.append(
                    '''update pangu_website.style_languages set `value` = "{}" where sl_id = {};'''.format(
                        i.get("tmp_value").strip(), i.get("sl_id")))
                self.resData2.append(
                    '''update pangu_website.style_languages set `value` = "{}" where sl_id = {};'''.format(
                        i.get("value"), i.get("sl_id")))

    def fixPanAttribute(self):
        print("pangu attribute language")
        sql = PanGuTable(index="getPanAttributeDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="panGuWebPron",
                  ).getAll()
        if len(data) > 0:
            for i in data:
                self.resData.append(
                    '''update pangu.attribute_languages set `value` = "{}" where id = {};'''.format(
                        i.get("tmp_value").strip(), i.get("id")))
                self.resData2.append(
                    '''update pangu.attribute_languages set `value` = "{}" where id = {};'''.format(
                        i.get("value"), i.get("id")))

    def fixPanStyle(self):
        print("pangu style language")
        sql = PanGuTable(index="getPanStyleDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="panGuWebPron",
                  ).getAll()
        if len(data) > 0:
            for i in data:
                self.resData.append(
                    '''update pangu.style_languages set `value` = "{}" where id = {};'''.format(
                        i.get("tmp_value").strip(), i.get("id")))
                self.resData2.append(
                    '''update pangu.style_languages set `value` = "{}" where id = {};'''.format(
                        i.get("value"), i.get("id")))

    def getImageColor(self):
        sql = PanGuTable(index="getValidationData").getSql()
        data = Db(sql=sql, param="','".join(self.param), db="panGuWebPron",
                  ).getAll()

        goodsMap = {}

        for i in data:
            goodsId = i.get("goods_id")
            if i.get("status") == 'FAILED':
                info = json.loads(i.get("result"))
                for k, v in info.get('medias').items():
                    sql = PanGuTable(index="getGoodsImageColor").getSql()
                    data = Db(sql=sql, param=(goodsId, k), db="panGuWebPron", showlog=True).getOne()
                    if goodsMap.get(goodsId) is not None:
                        goodsMap[goodsId].append(data.get('color'))
                    else:
                        goodsMap[goodsId] = [data.get('color')]

        for k, v in goodsMap.items():
            print(k, v)

    def fixGoodsScreenData(self):
        sql = PanGuTable(index="getPanScreenData").getSql()
        data = Db(sql=sql, param=(), db="panGuWebPron"
                  ).getAll()
        panguMap = {}
        for i in data:
            key = str(i.get("goods_id")) + i.get("img_url")
            panguMap[key] = {"gci_id": i.get("gci_id"), "s3_synced": i.get("s3_synced")}

        sql = websiteTable(index="getWebScreenData").getSql()
        data = Db(sql=sql, param=(), db="websitePron", ).getAll()
        webMap = {}
        for i in data:
            key = str(i.get("goods_id")) + i.get("img_url")
            webMap[key] = {"gci_id": i.get("gci_id"), "s3_synced": i.get("s3_synced")}

        diffList = []
        for k, v in panguMap.items():
            print(k, webMap.get(k))
            if webMap.get(k) is not None:
                if v.get("s3_synced") != webMap.get(k).get("s3_synced"):
                    diffList.append(webMap.get(k).get("gci_id"))

        print(diffList)

    def getShippingGoodsLog(self):
        sql = PanGuTable(index="getShippingGoodsLog").getSql()
        data = Db(sql=sql, param=(), db="websiteLogPron"
                  ).getAll()

        saveData = []

        for i in data:
            saveData.append(
                'insert into pangu_website.batch_operation_log(goods_id, `type`, old_data, new_data, `user`, create_at) values({}, 12, "", "{}","{}" ,"{}");'
                .format(i.get("goods_id"), i.get("content"), i.get("operator"), i.get("last_update_time")))
        File(path="../.././data/shippingGoodsLog.txt", txtData=saveData).writeTxt()

    def styleImgCheck(self):
        print("开始拉取盘古数据")
        sql = PanGuTable(index="getGoodsStyleImg").getSql()
        data = Db(sql=sql, param=(), db="panGuWebPron").getAll()
        panGuMap = {}
        for i in data:
            panGuMap[str(i.get('goods_id')) + str(i.get('style_id'))] = i

        print("开始拉取网站数据")
        webMap = {}
        sql = websiteTable(index="getGoodsStyleImg").getSql()
        data = Db(sql=sql, param=(), db="websitePron").getAll()
        for m in data:
            webMap[str(m.get('goods_id')) + str(m.get('style_id'))] = m

        goodsId = []
        for k, v in panGuMap.items():
            if webMap.get(k) is None:
                goodsId.append(v.get("goods_id"))

        print(goodsId)

    def downloadImg(self):
        data = File(path=self.param).read_excl()
        goodsMap = {}
        goodsList = []
        for i in data:
            goodsId = i[0]
            if goodsMap.get(goodsId) is not None:
                goodsMap.get(goodsId).append(i[2])
            else:
                goodsMap[goodsId] = [i[2]]
                goodsList.append(goodsId)

        newList = Array(target=goodsList, step=100).ArrayChunk()
        self.param3 = goodsMap
        MyThreading(num=20, data=newList, func=self.downGoodsImg).semaphoreJob()

    def downGoodsImg(self, data, desc, semaphore):
        print("开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        for i in data:
            print("开始下载商品 {} 图片".format(i))
            urlList = self.param3.get(i)
            self.save_image_from_url(urlList, i)

        print("线程 {} 处理结束".format(desc))
        # 释放锁
        semaphore.release()

    def save_image_from_url(self, urlList, goodsId):
        PanGu.ensure_directory_exists("E:/MY_PROJECT/PYTHON/python-toolBox/data/goods_plus_img/" + str(goodsId))
        num = 1
        for url in urlList:
            """下载图片并保存到指定路径"""
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                with open("E:/MY_PROJECT/PYTHON/python-toolBox/data/goods_plus_img/" + str(goodsId) + "/" + str(
                        num) + ".jpg", 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            except requests.RequestException as e:
                print(f"Error downloading image from {url}: {e}")
                return None
            num = num + 1

    @staticmethod
    def ensure_directory_exists(directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        else:
            print(f"Directory '{directory_path}' already exists.")

    def styleImgFix(self):

        sql = PanGuTable(index="getStyleImgByCat").getSql()
        data = Db(sql=sql, param=",".join(self.param), db="panGuWebPron", showlog=True).getAll()
        self.resData = {}
        for i in data:
            self.resData[i.get('goods_id')] = {"cat_id": i.get("cat_id"), "num": i.get("num")}

        print(len(self.resData))

        newList = Array(target=list(self.resData.keys()), step=50).ArrayChunk()

        # 调用接口获取sku状态
        MyThreading(num=10, data=newList, func=self.getPanGuImgStyle).semaphoreJob()

        File(path=self.param2, fileData={0: self.resData2}, sheetName={0: "原商品与克隆商品截图差异"},
             sheetTitle={
                 0: ["原id", "原id品类", "原id截图数", "克隆id", "克隆id品类", "克隆id截图数"]}).writeExcel()

    def getPanGuImgStyle(self, data, desc, semaphore):
        print("获取style img 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        for i in data:
            sql = PanGuTable(index="getCloneId").getSql()
            data = Db(sql=sql, param=i, db="panGuWebPron").getAll()
            for m in data:
                sql = PanGuTable(index="getSonImgStyle").getSql()
                data = Db(sql=sql, param=m.get('id'), db="panGuWebPron").getOne()
                if data.get('num') is not None:
                    if data.get('num') != self.resData.get(i).get('num', 0):
                        self.resData2.append(
                            {"原id": i, "原id品类": self.resData.get(i).get('cat_id'), "克隆id": m.get('id'),
                             "克隆id品类": m.get('cat_id'), "原id截图数": self.resData.get(i).get('num', 0),
                             "克隆id截图数": data.get('num')})
        # 释放锁
        semaphore.release()
        print("获取style img 结束处理 {} 数据".format(desc))

    def inventoryStatistics(self):
        resMap = {}
        for k, v in self.param.items():
            res = []
            pskuList = []
            sql = PanGuTable(index="getStockData").getSql()
            data = Db(sql=sql, param=k, db="panguStockDb").getAll()
            for m in data:
                pskuList.append(m.get('psku'))
                res.append(self.calculateInventory(m))
            newList = Array(target=pskuList, step=500).ArrayChunk()
            # 调用接口获取sku状态
            MyThreading(num=10, data=newList, func=self.getPidInfo).semaphoreJob()
            for s in res:
                if self.resMap.get(s.get('psku')) is not None:
                    s['pid'] = self.resMap.get(s.get('sku'))
                else:
                    s['pid'] = ""
            resMap[v] = res

        File(path=self.path,
             fileData={0: resMap.get("UK"), 1: resMap.get("US"), 2: resMap.get("DE"), 3: resMap.get("AU"),
                       4: resMap.get("CA")},
             sheetName={0: 'UK', 1: 'US', 2: 'DE', 3: 'AU', 4: 'CA'},
             sheetTitle={0: ["psku", "sku_tag", "pid", "facility_id", "available_num", "available_tryon_num",
                             "available_sample_num"],
                         1: ["psku", "sku_tag", "pid", "facility_id", "available_num", "available_tryon_num",
                             "available_sample_num"],
                         2: ["psku", "sku_tag", "pid", "facility_id", "available_num", "available_tryon_num",
                             "available_sample_num"],
                         3: ["psku", "sku_tag", "pid", "facility_id", "available_num", "available_tryon_num",
                             "available_sample_num"],
                         4: ["psku", "sku_tag", "pid", "facility_id", "available_num", "available_tryon_num",
                             "available_sample_num"]
                         }).writeExcel()

    @staticmethod
    def calculateInventory(data):
        if Array(target=data.get("facility_id", 0), data=['1049275062', '2640152423', '2771772189', '3142292305']).InArray():
            print("不需特殊处理")
        elif data.get("sku_tag", 0) == '1':
            print("不需特殊处理")
        else:
            data['available_sample_num'] = data.get("available_sample_num", 0) + data.get("available_tryon_num", 0)
        return data

    def getPidInfo(self, data, desc, semaphore):

        print("获取 pid 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()

        sql = PanGuTable(index="getSkuPid").getSql()
        data = Db(sql=sql, param="','".join(data), db="panGuPron").getAll()
        for m in data:
            self.resMap[m.get("sku")] = m.get("pid")
        # 释放锁
        semaphore.release()
        print("获取pid 结束处理 {} 数据".format(desc))

    def tryOnAndSampleStatistics(self):
        resMap = {}
        for k, v in self.param.items():
            sql = PanGuTable(index="getClothsData").getSql()
            data = Db(sql=sql, param=k, db="panGuWebPron").getAll()
            pskuList = []
            for m in data:
                pskuList.append(m.get('psku'))
            newList = Array(target=pskuList, step=500).ArrayChunk()
            # 调用接口获取sku状态
            MyThreading(num=10, data=newList, func=self.getFacilityInfo).semaphoreJob()
            for s in data:
                if self.resMap.get(s.get('psku')) is not None:
                    s['facility_id'] = self.resMap.get(s.get('psku'))
                else:
                    s['facility_id'] = ""
            resMap[v] = data

        File(path=self.path,
             fileData={0: resMap.get("试衣"), 1: resMap.get("样衣")},
             sheetName={0: '试衣', 1: '样衣'},
             sheetTitle={0: ["gid", "pid", "sku", "psku", "color", "size", "small_cat", "cat_name",
                             "facility_id"],
                         1: ["gid", "pid", "sku", "psku", "color", "size", "small_cat", "cat_name",
                             "facility_id"]
                         }).writeExcel()
    def getFacilityInfo(self, data, desc, semaphore):
        print("获取 仓库 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()

        sql = PanGuTable(index="getSkuFacility").getSql()
        data = Db(sql=sql, param="','".join(data), db="panguStockDb").getAll()

        facilityList = {
            1049275062: 'UK',
            1049275063: 'US',
            2640152423: 'DE',
            2771772189: 'AU',
            3142292305: 'CA'
        }
        for m in data:
            self.resMap[m.get("sku")] = facilityList.get(m.get("facility_id"), "")
        # 释放锁
        semaphore.release()
        print("获取 仓库 结束处理 {} 数据".format(desc))

    def getColorMap(self):
        newColorMap = File(path=self.param).read_excl()
        tmpNewColorMap = {}
        for i in newColorMap:
            if tmpNewColorMap.get(i.get("颜色")) is not None:
                tmpNewColorMap.get(i.get("颜色")).append(i.get("PSKU"))
            else:
                tmpNewColorMap[i.get("颜色")] = [i.get("PSKU")]

        oldColorMap = File(path=self.path).read_excl()
        tmpOldColorMap = {}
        for i in oldColorMap:
            tmpOldColorMap[i.get("颜色")] = i.get("PSKU")

        mapRelation = []
        for k , v in tmpNewColorMap.items():
            for m in v:
                if tmpOldColorMap.get(k) is not None:
                    mapRelation.append({"color": k, "psku_old": tmpOldColorMap.get(k), "psku_new": m})
        print(len(mapRelation))
        exit()
        File(path="../.././data/色卡映射关系.xlsx", fileData={0: mapRelation}, sheetName={0: "色卡psku映射关系表"},
             sheetTitle={0: ["color", "psku_old", "psku_new"]}).writeExcel()
