import json
import math
import time

import pandas as pd

from common.commonMap import CommonMap
from model.tms import TmsTable
from model.wms import WmsTable
from pkg.db import Db
from pkg.emailC import Email
from pkg.erp import Erp
from tools.array import Array
from tools.curl import Curl
from tools.file import File
from tools.threadingTool import MyThreading


class Wms:
    def __init__(self, config=None, tableName=None, database=None, primary=None, warehouseId=None, psku=None,
                 index=None, path=None):
        self.config = config
        self.tableName = tableName
        self.database = database
        self.primary = primary
        self.resData = []
        self.specialData = []
        self.warehouseId = warehouseId
        self.psku = psku
        self.index = index
        self.path = path
        self.excelData = []
        self.initData = []
        self.skuPlatformSkuMapping = {}

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

    def inventoryCheck(self):
        erpInventoryMap = {}
        if self.warehouseId is not None:
            limit = 3000
            for k, v in self.warehouseId.items():
                print("开始处理仓库：{}".format(k))
                sql = WmsTable(index="getWarehouseCodeRecordNum").getSql()
                res = Db(sql=sql, db="db", param=k).getOne()
                warehouseRecodeNum = res.get('num', 0)
                offsetList = []
                if warehouseRecodeNum > 0:
                    num = 0
                    while num < warehouseRecodeNum:
                        offsetList.append({"offset": num, "limit": limit, "warehouse": k})
                        num += limit
                    # 开启多线程消费数据
                    MyThreading(num=10, data=offsetList, func=self.findInitData).semaphoreJob()
                else:
                    break
                # 获取erp库存信息
                erpTmpData = Erp(date={k: []}).getErpInventory()
                erpInventoryMap = erpInventoryMap.copy()
                erpInventoryMap.update(erpTmpData)

        targetList = Array(target=self.initData, step=1000).ArrayChunk()
        # 开启多线程消费数据
        MyThreading(num=10, data=targetList, func=self.comparedInventory).semaphoreJob()

        if len(self.resData) != 0:
            targetList = Array(target=self.resData, step=100).ArrayChunk()
            # 开启多线程消费数据
            MyThreading(num=10, data=targetList, func=self.analysisRes).semaphoreJob()
            if self.warehouseId is not None:
                if len(self.excelData) != 0:
                    tmpMap = {}
                    for s in self.excelData:
                        if tmpMap.get(s.get('analyze_reasons')) is None:
                            tmpMap[s.get('analyze_reasons')] = [s]
                        else:
                            tmpMap[s.get('analyze_reasons')].append(s)
                    tmpExcelData = []
                    for k, v in tmpMap.items():
                        for mm in v:
                            if self.skuPlatformSkuMapping.get(mm.get("sku")) is not None:
                                mm["platform_sku"] = self.skuPlatformSkuMapping.get(mm.get("sku"))
                            else:
                                mm["platform_sku"] = ''
                            tmpExcelData.append(mm)

                    # 合并 erp库存信息
                    newExcelData = []
                    for nn in tmpExcelData:
                        if erpInventoryMap.get(nn.get("platform_sku")) is not None:
                            nn["erp_new_num"] = erpInventoryMap.get(nn.get("platform_sku"))
                        else:
                            nn["erp_new_num"] = 0
                        newExcelData.append(nn)

                    File(path=self.path, fileData={0: newExcelData}, sheetName={0: "wms与tms库存对比表"},
                         sheetTitle={
                             0: ["sku", "platform_sku", "warehouse", "platform_code", "wms_inventory_new_num",
                                 "erp_new_num",
                                 "tms_inventory_num",
                                 "analyze_reasons", "remark", "need_fix"]}).writeExcel()
            else:
                tmpMap = {}
                for s in self.excelData:
                    tmpMap[s.get('sku')] = s
                return tmpMap

    def inventoryCompare(self):
        erpTmpData = Erp(warehouse="FFWH0036").getErpInventorySingle()
        data = []
        for i in erpTmpData:
            data.append(json.dumps(i))
        File(path="../.././data/bbb.txt", txtData=data).writeTxt()

    def analysisEmail(self):
        print("开始读取错误邮件信息！该过程需要几分钟请耐心等待......")
        # 读取文件类容
        emailData = File(path=self.path).read_txt()
        # 过滤数据
        dealData = []
        for i in emailData:
            if i[0].startswith("订单号："):
                mewTmp = i[0].split("timestamp:")
                dealData.append(mewTmp[0])
        # 去重数据
        newData = Array(data=dealData).ArrayUniq()
        # 提取数据
        targetData = []
        tmpMap = {}
        for m in newData:
            tmp = Array(data=m.split(" ")).ArrayFilter()
            if tmp[1] is None or tmp[2] is None:
                print("数据处理异常 {}".format(m))
            orderNo = tmp[0].split("：")[1]
            warehouseCode = CommonMap(target=int(tmp[1].split("：")[1])).warehouseMap()
            sku = tmp[2].split("(")[0]
            # 获取sku信息
            sql = WmsTable(index="getWmsGoodsInfo").getSql()
            goodsInfo = Db(sql=sql, db="db", param=(sku, warehouseCode)).getOne()
            if goodsInfo is None:
                sku = tmp[2].split("):")[0].split("(原：")[1]
                # 获取sku信息
                sql = WmsTable(index="getWmsGoodsInfo").getSql()
                goodsInfo = Db(sql=sql, db="db", param=(sku.strip(), warehouseCode)).getOne()
                if goodsInfo is not None:
                    self.initData.append(goodsInfo.get('sku'))
                targetData.append(
                    {"order_no": orderNo, 'sku': sku, 'warehouse_sku': goodsInfo.get('sku'), 'warehouse': warehouseCode,
                     "platform": goodsInfo.get('platform_code')})
                if tmpMap.get(warehouseCode) is None:
                    tmpMap[warehouseCode] = [sku]
                else:
                    tmpMap[warehouseCode].append(sku)
            else:
                self.initData.append(goodsInfo.get('sku'))
                targetData.append(
                    {"order_no": orderNo, 'sku': sku, 'warehouse_sku': goodsInfo.get('sku'), 'warehouse': warehouseCode,
                     "platform": goodsInfo.get('platform_code')})
                if tmpMap.get(warehouseCode) is None:
                    tmpMap[warehouseCode] = [sku]
                else:
                    tmpMap[warehouseCode].append(sku)

        analysisData = self.inventoryCheck()

        print("开始请求erp 获取库存数据")
        erpInventoryMap = Erp(date=tmpMap).getErpInventory()

        resData = []
        for i in targetData:
            if analysisData is not None:
                if analysisData.get(i.get('warehouse_sku')) is not None:
                    resData.append({"订单号": i.get("order_no"), "sku": i.get("sku"), "仓库sku": i.get("warehouse_sku"),
                                    "仓库": i.get("warehouse"), "平台": i.get("platform"),
                                    "wms全新库存": analysisData.get(i.get('warehouse_sku')).get("wms_inventory_new_num"),
                                    "erp全新库存": erpInventoryMap.get(i.get("sku", 0)),
                                    "proxy库存": analysisData.get(i.get('warehouse_sku')).get("tms_inventory_num"),
                                    "分析原因": analysisData.get(i.get('warehouse_sku')).get("analyze_reasons"),
                                    "是否需要处理": analysisData.get(i.get('warehouse_sku')).get("need_fix")})

                else:
                    tmpData = self.getSkuInventoryData(i.get("sku"), i.get("warehouse_sku"), erpInventoryMap)
                    resData.append({"订单号": i.get("order_no"), "sku": i.get("sku"), "仓库sku": i.get("warehouse_sku"),
                                    "仓库": i.get("warehouse"), "平台": i.get("platform"),
                                    "wms全新库存": tmpData.get("new_num", "暂无数据"),
                                    "erp全新库存": erpInventoryMap.get(i.get("sku", 0), 0),
                                    "proxy库存": tmpData.get("num", "暂无数据"),
                                    "分析原因": tmpData.get("analysis"),
                                    "是否需要处理": tmpData.get("res")})
            else:
                tmpData = self.getSkuInventoryData(i.get("sku"), i.get("warehouse_sku"), erpInventoryMap)
                resData.append({"订单号": i.get("order_no"), "sku": i.get("sku"), "仓库sku": i.get("warehouse_sku"),
                                "仓库": i.get("warehouse"), "平台": i.get("platform"),
                                "wms全新库存": tmpData.get("new_num", "暂无数据"),
                                "erp全新库存": erpInventoryMap.get(i.get("sku", 0), 0),
                                "proxy库存": tmpData.get("num", "暂无数据"),
                                "分析原因": tmpData.get("analysis"),
                                "是否需要处理": tmpData.get("res")})

        print("写入分析结果！")

        filePath = "../.././data/analysisEmail.xlsx"
        File(path=filePath, fileData={0: resData}, sheetName={0: "发货单同步WMS失败原因分析表"},
             sheetTitle={
                 0: ["订单号", "sku", "仓库sku", "仓库", "平台", "wms全新库存", "erp全新库存", "proxy库存", "分析原因", "是否需要处理"]
             }).writeExcel()

        print("开始发送处理结果邮件！")
        Email(title="发货单同步WMS失败原因分析", content="分析结果见 excel", receiver=["muhe@kerrylan.com"],
              fileName="analysisEmail.xlsx",
              filePath=filePath, deleteStatus=False).sendEmail()
        print("服务结束！")

    def comparedInventory(self, data, desc, semaphore):
        print("查询库存 多线程消费： {} 数据".format(desc))
        # 上锁
        semaphore.acquire()

        wmsInventoryMap = {}
        tmsInventoryMap = {}

        # 查询wms库存信息
        sql = WmsTable(index="getWmsInventoryNum").getSql()
        wmsTmpData = Db(sql=sql, db="db", param=("','".join(data))).getAll()
        if wmsTmpData is not None:
            for i in wmsTmpData:
                wmsInventoryMap[i.get("sku")] = i
        # 查询tms库存信息
        sql = TmsTable(index="getTmsInventoryNum").getSql()
        tmsTmpData = Db(sql=sql, db="proxy_db", param=("','".join(data))).getAll()

        if tmsTmpData is not None:
            for i in tmsTmpData:
                tmsInventoryMap[i.get("sku")] = i

        # 比较数据
        for k, v in wmsInventoryMap.items():
            if tmsInventoryMap.get(k) is not None:
                if v.get('new_num', 0) + v.get('second_num', 0) != tmsInventoryMap.get(k).get('num', 0):
                    self.resData.append(
                        {"sku": k, "warehouse": v.get('warehouse_code', ""), "platform_code": v.get("platform_code"),
                         "wms_inventory_new_num": v.get('new_num', 0),
                         "wms_inventory_second_num": v.get('second_num', 0),
                         "tms_inventory_num": tmsInventoryMap.get(k).get('num', 0)})
            else:
                self.resData.append(
                    {"sku": k, "warehouse": v.get('warehouse_code', ""), "platform_code": v.get("platform_code"),
                     "wms_inventory_new_num": v.get('new_num', 0), "wms_inventory_second_num": v.get('second_num', 0),
                     "tms_inventory_num": 0})

        # 释放锁
        semaphore.release()

    def analysisRes(self, data, desc, semaphore):
        print("分析原因多线程消费： {} 数据".format(desc))
        # 上锁
        semaphore.acquire()

        for n in data:
            print("分析原因多线程 {} 开始分析sku：{} 异常原因".format(desc, n.get("sku")))
            if n.get('platform_code') == "VV":
                n['analyze_reasons'] = 'vv商品报废'
                n['remark'] = ""
                n['need_fix'] = "否"
                # self.excelData.append(n)
                continue
            # 判断是否存在二手库存
            if n.get('wms_inventory_new_num') == n.get('tms_inventory_num', 0):
                n['analyze_reasons'] = 'wms 存在二手库存'
                n['remark'] = ""
                n['need_fix'] = "否"
                # self.excelData.append(n)
                continue
            #  计算刷数总数
            sql = WmsTable(index="fix_data_check").getSql()
            fixDataRes = Db(sql=sql, db="db", param=(n.get('sku'))).getOne()
            if fixDataRes is not None:
                if fixDataRes.get('num') is not None and fixDataRes.get('num') > n.get('tms_inventory_num', 0):
                    n['analyze_reasons'] = "刷数导致数据异常"
                    n['remark'] = ''
                    n['need_fix'] = "是"
                    self.excelData.append(n)
                    continue

            # 判断是否是品类合并导致数据异常
            if n.get('sku', '').startswith("wmsskuc"):
                n['analyze_reasons'] = "品类数据合并 proxy库存数据异常"
                n['remark'] = ''
                n['need_fix'] = "是"
                self.excelData.append(n)
                continue

            if Array(target=n.get('tms_inventory_num', 0), data=[-1, 1]).InArray():
                n['analyze_reasons'] = 'proxy 历史数据异常'
                n['remark'] = ""
                n['need_fix'] = "是"
                self.excelData.append(n)
                continue

            if n.get('tms_inventory_num', 0) == 0:
                n['analyze_reasons'] = 'proxy 数据缺失'
                n['remark'] = ""
                n['need_fix'] = "是"
                self.excelData.append(n)
                continue

            n['analyze_reasons'] = '暂未分析出原因'
            n['remark'] = ""
            n['need_fix'] = ""
            self.excelData.append(n)

        # 释放锁
        semaphore.release()

    def findInitData(self, data, desc, semaphore):
        print("获取原始数据多线程消费： {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        sql = WmsTable(index="getSkuList").getSql()
        data = Db(sql=sql, db="db", param=(data.get('warehouse'), data.get('limit'), data.get('offset'))).getAll()
        for i in data:
            self.initData.append(i.get('sku'))
            self.skuPlatformSkuMapping[i.get('sku')] = i.get('platform_sku')

        # 释放锁
        semaphore.release()

    @staticmethod
    def getSkuInventoryData(platformSku, warehouseSku, erpInventoryMap):
        # 获取wms 库存数据
        sql = WmsTable(index="getWmsInventoryNum").getSql()
        wmsTmpData = Db(sql=sql, db="db", param=warehouseSku).getOne()
        if wmsTmpData is None:
            wmsTmpData = {"new_num": "暂无数据", "second_num": "暂无数据"}
        # 查询tms库存信息
        sql = TmsTable(index="getTmsInventoryNum").getSql()
        tmsTmpData = Db(sql=sql, db="proxy_db", param=warehouseSku).getOne()
        if tmsTmpData is None:
            tmsTmpData = {"num": "暂无数据"}
        if erpInventoryMap.get(platformSku, 0) == wmsTmpData.get("new_num", 0) and wmsTmpData.get(
                "new_num",
                0) == tmsTmpData.get("num", 0):
            # 检查报错sku是否存在未发货的订单
            sql = TmsTable(index="getNotShippedOrderBySkuId").getSql()
            orderInfo = Db(sql=sql, db="proxy_db", param=warehouseSku).getAll()
            if orderInfo is None:
                analysisRes = "数据已修复"
                dealRes = "否"
            elif len(orderInfo) == 0:
                analysisRes = "数据已修复"
                dealRes = "否"
            else:
                shipmentNumber = []
                waybillNumber = []
                for ss in orderInfo:
                    shipmentNumber.append(ss.get('last_mile_order_sn'))
                    waybillNumber.append(ss.get('platform_shipping_sn'))

                analysisRes = "存在未发货订单：(发货单号：{} 运单号： {})".format(",".join(shipmentNumber),
                                                                 ",".join(waybillNumber))
                dealRes = "业务人员处理"
        else:
            analysisRes = "历史数据缺失"
            dealRes = "是"
        return {"new_num": wmsTmpData.get("new_num"), "num": tmsTmpData.get("num"), "analysis": analysisRes,
                "res": dealRes}



