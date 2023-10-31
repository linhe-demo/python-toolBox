from model.erp import ErpDatatable
from pkg.db import Db
from tools.file import File


class Erp:
    def __init__(self, filePath=None):
        self.filePath = filePath

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
