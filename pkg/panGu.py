import json
import time

from model.panGu import PanGuTable
from pkg.db import Db
from tools.array import Array
from tools.curl import Curl
from tools.file import File
from tools.show import Show
from tools.sqlTool import SqlTool
from tools.threadingTool import MyThreading


class PanGu:
    def __init__(self, param=None, param2=None, path=None, limit=None, offset=None):
        self.param = param
        self.param2 = param2
        self.path = path
        self.resData = []
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