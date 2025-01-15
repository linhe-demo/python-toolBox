import calendar
import datetime
import json
import math
import time

from common.warehouseEnum import WarehouseEnum
from model.erp import ErpDatatable
from model.panGu import PanGuTable
from pkg.db import Db
from pkg.highcharts import Highcharts
from tools import curl
from tools.array import Array
from tools.curl import Curl
from tools.file import File
from tools.log import Log
from tools.threadingTool import MyThreading


class Erp:
    def __init__(self, filePath=None, warehouse=None, orderSn=None, date=None, param=None):
        self.param = param
        self.filePath = filePath
        self.orderSn = orderSn
        self.warehouse = warehouse
        self.type = WarehouseEnum
        self.date = date
        self.res = {}
        self.excelData = []
        self.skuData = {}
        self.noSaleList = {}

    def checkSkuExists(self):
        data = File(path=self.filePath).read_txt()
        if len(data) == 0:
            print("目标数据为空")

        notExistList = []

        for i in data:
            sql = ErpDatatable(index="check_sku_exist").getSql()
            tmp = Db(sql=sql, param=i[0], db="erp_db_prod").getAll()
            if len(tmp) == 0:
                notExistList.append(i[0])
                print(i[0])

        if len(notExistList) > 0:
            File(path="../.././data/notExist.txt", txtData=notExistList).writeTxt()

    def transfer(self):
        if self.orderSn is None or len(self.orderSn) == 0:
            print("采购单号不能为空！")
            return
        if self.warehouse is None or self.warehouse == 0:
            print("仓库信息不能为空！")
            return
        # 查询订单详情
        sql = ErpDatatable(index="get_order_info").getSql()
        data = Db(sql=sql, param=self.orderSn, db="erp_db_prod").getAll()
        orderIdList = []
        sqlList = []
        if data is None:
            return
        for i in data:
            if self.warehouse != int(i.get('facility_id', 0)):
                sql = ErpDatatable(index="update_order_info").getSql() % (self.warehouse, i.get('order_id'))
                sqlList.append(sql)
                orderIdList.append(str(i.get('order_id')))

        if len(orderIdList) == 0:
            print("采购单当前仓库与需要转换的仓库一致，不允许转换！")
            return
        # 批量采购详情
        sql = ErpDatatable(index="get_purchase_info").getSql()
        data = Db(sql=sql, param="','".join(orderIdList), db="erp_db_prod").getAll()
        for i in data:
            if self.warehouse != int(i.get('facility_id', 0)):
                sql = ErpDatatable(index="update_purchase_info").getSql() % (self.warehouse, i.get('order_id'))
                sqlList.append(sql)
        # 如果已收货 发货明细数据也需修改
        sql = ErpDatatable(index="get_delivery_info").getSql()
        data = Db(sql=sql, param="','".join(orderIdList), db="erp_db_prod").getAll()
        for i in data:
            if self.warehouse != i.get('facility_id', 0):
                sql = ErpDatatable(index="update_delivery_info").getSql() % (self.warehouse, i.get('order_id'))
                sqlList.append(sql)

        for i in sqlList:
            print(i)

    def getOrderInfo(self):
        x_data = []
        tmp_x_data = {}
        y_data = []
        for year in self.date:
            print("开始处理 {} 数据".format(year))
            # 循环遍历每个月
            tmpY = []
            for month in range(1, 13):
                # 获取当前月份的第一天和最后一天
                first_month_day = datetime.date(year, month, 1)
                last_month_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
                sql = ErpDatatable(index="get_order_info_money").getSql()
                data = Db(sql=sql, param=(first_month_day, last_month_day), db="erp_db_prod").getOne()
                tmp_x_data[month] = "{}月".format(month)
                if data is None:
                    tmpY.append(0)
                else:
                    tmpY.append(data.get('t'))

                print("{} 月数据已处理".format(month))

            y_data.append({"name": year, "data": tmpY})

        for k, v in tmp_x_data.items():
            x_data.append(v)

        Highcharts(tableType="line", name="chart", title="订单金额图", x_data=x_data, y_data=y_data).draw()

    def getErpInventory(self):
        erpInventoryMap = {}
        for k, v in self.date.items():
            tmpTime = math.ceil(time.time())
            print("开始获取 仓库{} 数据".format(k))
            # 开始获取 erp 库存信息
            info = Curl(method="Apiv1/Wms/sku/inventory",
                        param={"warehouseCode": k, "platformCode": "JJ", "sku": ",".join(v), "time": str(tmpTime)},
                        timestamp=tmpTime).getErpStockInfo()

            if info is not None and len(info) > 0:
                for s in info:
                    erpInventoryMap[s.get('goods_sn')] = s.get('new_num')
        return erpInventoryMap

    def getErpInventorySingle(self):
        tmpTime = math.ceil(time.time())
        info = Curl(method="Apiv1/Wms/sku/inventory",
                    param={"warehouseCode": self.warehouse, "platformCode": "JJ", "sku": "", "time": str(tmpTime)},
                    timestamp=tmpTime).getErpStockInfo()

        key = info.get("key")
        tims = 0
        erpInventoryMap = []
        if len(key) > 0:
            while True:
                tmpTime = math.ceil(time.time())
                print("开始拉取库存信息 时间：".format(tims))
                time.sleep(60)
                tims = tims + 60
                data = Curl(method="Apiv1/Wms/sku/statistics",
                            param={"key": key, "time": str(tmpTime)},
                            timestamp=tmpTime).getErpStockInfo()
                if len(data.get('list')) > 0:
                    erpInventoryMap = data.get('list')
                    break
        return erpInventoryMap

    @staticmethod
    def getGoodsIdBySku(s):
        index_g = s.find('g')
        index_y = s.find('y')
        index_s = s.find('s')

        # 检查是否找到了这两个字符，并且'g'在'y'之前
        if index_g != -1 and index_y != -1 and index_g < index_y:
            goodsId = str(s[index_g + 1:index_y])
            if goodsId.isdigit():
                return goodsId
            else:
                return 0
        else:
            if index_g != -1 and index_s != -1 and index_g < index_s:
                goodsId = str(s[index_g + 1:index_y])
                if goodsId.isdigit():
                    return goodsId
                else:
                    return 0
            else:
                return 0

    def getSkuStatus(self):
        # 获取需要处理的sku
        sql = ErpDatatable(index="getSku").getSql()
        data = Db(sql=sql, param=self.param, db="erp_db_prod", writeLog=True).getAll()
        specialSku = []

        print("本次处理的sku总个数：{}".format(len(data)))
        for i in data:
            goodsId = self.getGoodsIdBySku(i.get('uniq_sku'))
            if goodsId == 0:
                specialSku.append(i.get('uniq_sku'))
            if self.skuData.get(str(goodsId)) is not None:
                self.skuData.get(str(goodsId)).append(i.get('uniq_sku'))
            else:
                self.skuData[str(goodsId)] = [i.get('uniq_sku')]

        GoodsList = list(self.skuData.keys())
        print("本次共处理商品id个数：{}".format(len(GoodsList)))
        skuStatusList = []

        # 获取已下架的商品ID
        newList = Array(target=GoodsList, step=500).ArrayChunk()

        MyThreading(num=4, data=newList, func=self.getGoodsShelfStatus).semaphoreJob()
        print(len(self.noSaleList))
        for k, v in self.skuData.items():
            if self.noSaleList.get(str(k)) is not None:
                for m in v:
                    skuStatusList.append("insert into tmp_sku (sku, status) values ('%s', 0);" % m)
            else:
                for n in v:
                    specialSku.append(n)

        print("已处理不在架sku个数：{}".format(len(skuStatusList)))

        print("本次需要额外处理的sku个数：{}".format(len(specialSku)))
        tmpNewList = Array(target=specialSku, step=400).ArrayChunk()

        # 调用接口获取sku状态
        MyThreading(num=3, data=tmpNewList, func=self.getPanGuSkuStatus).semaphoreJob()

        for s in self.excelData:
            skuStatusList.append(s)

        print(len(skuStatusList))

        File(path="../.././data/skuStatus.txt", txtData=skuStatusList).writeTxt()

    def getGoodsShelfStatus(self, data, desc, semaphore):
        # print("获取商品不在架 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        sql = PanGuTable(index="getGoodsStatus").getSql()
        res = Db(sql=sql, param="','".join(data), db="panGuWebPron", writeLog=True).getAll()
        for i in res:
            self.noSaleList[str(i.get('id'))] = i.get('id')
        # 释放锁
        semaphore.release()
        # print("获取商品不在架 结束处理 {} 数据".format(desc))
    def getPanGuSkuStatus(self, data, desc, semaphore):
        print("获取sku在架情况 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        res = Curl(url="https://pangu.smaloo.com/api/erp/skuStatus",
                   param=json.dumps({"web_skus": data})).panGuSkuStatus()
        tmpData = json.loads(res)
        if tmpData.get('code') == 200:
            for m in data:
                if tmpData.get('data').get(m) is not None:
                    self.excelData.append(
                        "insert into tmp_sku (sku, status) values ('{}', {});".format(m, tmpData.get('data').get(m)))
                else:
                    self.excelData.append(
                        "insert into tmp_sku (sku, status) values ('{}', 2);".format(m))
        print("获取sku在架情况 {} 处理结束".format(desc))
        # 释放锁
        semaphore.release()
