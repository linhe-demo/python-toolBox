import calendar
import datetime
import math
import time

from common.warehouseEnum import WarehouseEnum
from model.erp import ErpDatatable
from pkg.db import Db
from pkg.highcharts import Highcharts
from tools.curl import Curl
from tools.file import File


class Erp:
    def __init__(self, filePath=None, warehouse=None, orderSn=None, date=None):
        self.filePath = filePath
        self.orderSn = orderSn
        self.warehouse = warehouse
        self.type = WarehouseEnum
        self.date = date

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
                            param={"key": key,"time": str(tmpTime)},
                            timestamp=tmpTime).getErpStockInfo()
                if len(data.get('list')) > 0:
                    erpInventoryMap = data.get('list')
                    break
        return erpInventoryMap
