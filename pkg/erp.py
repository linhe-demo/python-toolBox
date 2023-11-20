from common.warehouseEnum import WarehouseEnum
from model.erp import ErpDatatable
from pkg.db import Db
from tools.file import File


class Erp:
    def __init__(self, filePath=None, warehouse=None, orderSn=None):
        self.filePath = filePath
        self.orderSn = orderSn
        self.warehouse = warehouse
        self.type = WarehouseEnum

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
        for i in data:
            if self.warehouse != int(i.get('facility_id', 0)):
                sql = ErpDatatable(index="update_order_info").getSql() % (self.warehouse, i.get('order_id'))
                print("订单仓库修改sql: {}".format(sql))
                orderIdList .append(str(i.get('order_id')))

        if len(orderIdList) == 0:
            print("采购单当前仓库与需要转换的仓库一致，不允许转换！")
            return
        # 批量采购详情
        sql = ErpDatatable(index="get_purchase_info").getSql()
        data = Db(sql=sql, param="','".join(orderIdList), db="erp_db_prod").getAll()
        for i in data:
            if self.warehouse != int(i.get('facility_id', 0)):
                sql = ErpDatatable(index="update_purchase_info").getSql() % (self.warehouse, i.get('order_id'))
                print("批量采购仓库修改sql: {}".format(sql))
        # 如果已收货 发货明细数据也需修改
        sql = ErpDatatable(index="get_delivery_info").getSql()
        data = Db(sql=sql, param="','".join(orderIdList), db="erp_db_prod").getAll()
        for i in data:
            if self.warehouse != i.get('facility_id', 0):
                sql = ErpDatatable(index="update_delivery_info").getSql() % (self.warehouse, i.get('order_id'))
                print("发货明细仓库修改sql: {}".format(sql))

