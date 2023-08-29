import time

from model.panGu import PanGuTable
from pkg.db import Db
from tools.array import Array
from tools.file import File
from tools.threadingTool import MyThreading


class PanGu:
    def __init__(self, param=None, path=None):
        self.param = param
        self.path = path
        self.resData = []

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
