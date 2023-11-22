import pandas as pd

from model.wms import WmsTable
from pkg.db import Db
from tools.array import Array
from tools.file import File
from tools.threadingTool import MyThreading


class Wms:
    def __init__(self, config=None, tableName=None, database=None, primary=None):
        self.config = config
        self.tableName = tableName
        self.database = database
        self.primary = primary
        self.resData = []
        self.specialData = []

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
                sql = "INSERT INTO fw_in_stock_age(`sku`, `num`, `inventory_type`, `status`, `create_time`) VALUES('%s', %s, %s, %s, '%s');" % (m.get('sku'), m.get('num'), m.get('inventory_type'), m.get('status'), m.get('create_time'))
                self.resData.append(sql)
                # if m.get('create_time') == '2023-11-22 00:00:00' and m.get('sku').startswith('wmsskuc') is False:
                #     self.specialData.append(m.get('sku'))
        # 释放锁
        semaphore.release()
