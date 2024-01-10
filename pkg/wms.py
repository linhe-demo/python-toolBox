import pandas as pd

from model.wms import WmsTable
from pkg.db import Db
from tools.array import Array
from tools.file import File
from tools.threadingTool import MyThreading


class Wms:
    def __init__(self, config=None, tableName=None, database=None, primary=None, warehouseId=None, psku=None, index=None):
        self.config = config
        self.tableName = tableName
        self.database = database
        self.primary = primary
        self.resData = []
        self.specialData = []
        self.warehouseId = warehouseId
        self.psku = psku
        self.index = index

    def dealTableData(self):
        configList = self.config.split(",")

        insertStatements = []
        updateLIst = []
        updateStatements = []
        for i in configList:
            sql = WmsTable(index="getCategoryData").getSql()
            data = Db(sql=sql, param=(self.tableName, "'c" + i + "g%'"), db="db").getAll()

            df = pd.DataFrame(data)

            tableName = self.tableName
            columns = ', '.join(df.columns)

            tmpUpdateList = []
            for index, row in df.iterrows():
                tmpUpdateList.append(str(row.get(self.primary)))
                values = ', '.join(f"'{str(value)}'" for value in row.values)
                insertStatement = f"INSERT INTO {self.database}.{tableName} ({columns}) VALUES ({values});"
                insertStatements.append(insertStatement)
            if len(tmpUpdateList) > 0:
                updateLIst.append(tmpUpdateList)

        # 组装更新语句
        for i in updateLIst:
            update = f"UPDATE {self.database}.{tableName} SET abnormal_mark = 'SECOND' where {self.primary} IN (%s) ;"
            updateStatements.append(update % ",".join(i))

        # 写入数据
        File(path="../.././data/bk.txt", txtData=insertStatements).writeTxt()
        File(path="../.././data/update.txt", txtData=updateStatements).writeTxt()

    def inventoryAgeInitQuery(self):
        sql = WmsTable(index="getInventoryAgeSkuList").getSql()
        data = Db(sql=sql, param=(), db="db").getAll()
        skuList = []
        for i in data:
            skuList.append(i.get('sku'))

        targetList = Array(target=skuList, step=1000).ArrayChunk()

        # 开启多线程消费数据
        MyThreading(num=10, data=targetList, func=self.getInventoryAge).semaphoreJob()

        # 将结果数据写入文件
        File(path="../.././data/inventoryAgeSql.txt", txtData=self.resData).writeTxt()

        # print("','".join(self.specialData))

    def getInventoryAge(self, data, desc, semaphore):
        # 上锁
        semaphore.acquire()
        if len(data) > 0:
            print("开始处理 {} 数据".format(desc))
            sql = WmsTable(index="getInventoryAgeInitData").getSql()
            data = Db(sql=sql, param="','".join(data), db="db").getAll()
            for m in data:
                sql = "INSERT INTO fw_in_stock_age(`sku`, `num`, `inventory_type`, `status`, `create_time`) VALUES('%s', %s, %s, %s, '%s');" % (
                    m.get('sku'), m.get('num'), m.get('inventory_type'), m.get('status'), m.get('create_time'))
                self.resData.append(sql)
                # if m.get('create_time') == '2023-11-22 00:00:00' and m.get('sku').startswith('wmsskuc') is False:
                #     self.specialData.append(m.get('sku'))
        # 释放锁
        semaphore.release()

    def createLog(self):
        inventoryLog = []
        stockAgeLog = []
        tmpList = []
        sql = WmsTable(index="getMovePsku").getSql()
        data = Db(sql=sql, db="db", param=("','".join(self.psku), self.warehouseId)).getAll()
        for m in data:
            sql = WmsTable(index="getNewInventory").getSql()
            info = Db(sql=sql, db="db", param=(m.get('sku'), m.get('location_code'))).getOne()
            if info is None:
                continue
            print(m)
            inventoryLogSql = WmsTable(index="insertInventoryLog").getSql().format(
                1311469176121118722 + m.get('id'),
                info.get('id'),
                info.get('sku'),
                info.get('warehouse_code'),
                info.get('location_code'),
                info.get('platform_code'),
                info.get('container_code', ''),
                info.get('po_no', ''),
                info.get('status'),
                info.get('sales_status'),
                info.get('quality'),
                'FIXDATA',
                '20231222181012666666',
                '20231222181012666666',
                0,
                info.get('available_qty'),
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                '2024-01-05 16:49:00',
                'sys',
                '2024-01-05 16:49:00',
                'sys'
            )
            inventoryLog.append(inventoryLogSql)

            # 检查库龄数据是否存在
        #     sql = WmsTable(index="getStockAge").getSql()
        #     stockAgeInfo = Db(sql=sql, db="db", param=(m.get('sku'))).getOne()
        #     if stockAgeInfo is None:
        #         # tmpSql = WmsTable(index="insertStockAgeLog").getSql().format(
        #         #     info.get('sku'), info.get('available_qty'), 0, 1, '2023-12-22 18:14:00', '2023-12-22 18:14:00')
        #         tmpList.append(1111111)
        #     else:
        #         tmpSql = "UPDATE ff_wms.fw_in_stock_age SET num = num + {} WHERE id = {}".format(info.get('available_qty'), stockAgeInfo.get('id'))
        #         tmpList.append(str(stockAgeInfo.get('id')))
        #     # stockAgeLog.append(tmpSql)
        # # 将结果数据写入文件
        resData = inventoryLog + stockAgeLog
        File(path="../.././data/moveLogSql.txt", txtData=resData).writeTxt()

    def fixBarcode(self):
        sql = WmsTable(index="getGoodsSkuBk").getSql()
        data = Db(sql=sql, db="db", param=()).getAll()
        targetList = Array(target=data, step=100).ArrayChunk()

        # 开启多线程消费数据
        MyThreading(num=10, data=targetList, func=self.getFixBarcodeSql).semaphoreJob()

        # 将结果数据写入文件
        File(path="../.././data/fixBarcode.txt", txtData=self.resData).writeTxt()

    def getFixBarcodeSql(self, data, desc, semaphore):
        print("开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        for i in data:
            # 检查PskuMapping 表是否存在映射数据
            sql = WmsTable(index="getPskuMapping").getSql()
            data = Db(sql=sql, db="db", param=(i.get('platform_sku'))).getOne()
            if data is not None:
                if data.get('barcode', '') != i.get('barcode'):
                    sql = "UPDATE  `ff_wms`.fw_psku_mapping SET barcode = '{}' WHERE id = {}".format(i.get('barcode'),
                                                                                                     data.get('id'))
                    print(sql)
                    self.resData.append(sql)
        # 释放锁
        semaphore.release()
