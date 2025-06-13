import calendar
import json
import math
import time
from datetime import datetime, timedelta

from bson import ObjectId

from model.fdfd import FdfdTable
from pkg.db import Db
from pkg.mogo import Mogo
from tools.array import Array
from tools.curl import Curl
from tools.file import File
from tools.threadingTool import MyThreading


class Fdfd:
    def __init__(self, param=None, path=None, year=None, holidays=None, tx_day=None, operation_type=None):
        self.param = param
        self.totalTime = 0
        self.result = []
        self.path = path
        self.year = year
        self.holidays = holidays
        self.tx_day = tx_day
        self.tmpMap = {}
        self.chatMap = {}
        self.operationType = operation_type

    def testInterfaceSpeed(self):
        list = []

        for i in range(0, 100):
            list.append(i)

        newList = Array(target=list, step=10).ArrayChunk()

        # 启用多携程发送消息
        MyThreading(num=10, data=newList, func=self.sendMessage).semaphoreJob()

        averageUseTime = self.totalTime / len(list)
        self.result.append("总请求次数：{} 平均用时：{}".format(len(list), averageUseTime))

        File(path=self.path, txtData=self.result).writeTxt()

    def calculateDate(self):
        cal = calendar.Calendar()
        year_days = []

        for month in range(1, 13):
            # 获取该月所有天数（包括前后月的填充）
            month_days = cal.monthdays2calendar(self.param, month)
            for week in month_days:
                for day, weekday in week:
                    if day != 0:  # 0 表示非当前月的填充日
                        if (weekday == 0) or (weekday == 6):
                            type = 1
                        else:
                            type = 0
                        data = {"year": self.param, "month": month, "day": "{}-{}-{}".format(self.param, month, day),
                                "weekday": weekday, "type": type}
                        print(data)
                        year_days.append(data)
        return year_days

    def get_year_days_with_holidays(self):
        """
        获取某年所有日期的月份、星期几及是否法定节假日

        :param year: 年份（如2023）
        :param holidays: 自定义节假日列表，格式为["YYYY-MM-DD"]
        :return: 包含日期信息的字典列表
        """
        if self.holidays is None:
            # 中国法定节假日（示例数据，需自行维护更新）
            holidays = [
                f"{self.year}-01-01",  # 元旦
                f"{self.year}-05-01",  # 劳动节
                f"{self.year}-10-01",  # 国庆节
                # 添加其他法定节假日...
            ]

        start_date = datetime(self.year, 1, 1)
        end_date = datetime(self.year + 1, 1, 1)

        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        result = []

        current_date = start_date
        while current_date < end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            is_holiday = date_str in self.holidays
            is_weekend = current_date.weekday() >= 5  # 5和6是周六日

            if is_holiday:
                dayType = 2
            elif is_weekend:
                dayType = 1
            else:
                dayType = 0

            if current_date.weekday() == 6:
                day = 0
            else:
                day = current_date.weekday() + 1

            if Array(target=date_str, data=self.tx_day).InArray():
                dayType = 0

            result.append({
                "day_str": date_str,
                "year": current_date.year,
                "month": current_date.month,
                "week_en": day,
                "type": dayType,
                "is_holiday": is_holiday,
                "is_weekend": is_weekend,
                "is_legal_holiday": is_holiday  # 简单判断逻辑
            })

            current_date += timedelta(days=1)

        # 获取测试服日期数据
        sql = FdfdTable(index="getWorkDay").getSql()
        data = Db(sql=sql, param=self.year, db="fdfdTest").getAll()
        num = 0
        for v in data:
            tmp = result[num]
            if v.get("type") != tmp.get("type"):
                print(tmp, v)
            num = num + 1

        return result

    def sendMessage(self, data, desc, semaphore):
        print("发送消息给用户 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        for i in data:
            millisecondsBegin = time.time_ns() // 1_000_000
            res = Curl(url="https://api.oa.fdttgroup.com/api/user/send-notice",
                       param=json.dumps(self.param)).panGuSkuStatus()
            millisecondsEnd = time.time_ns() // 1_000_000
            useTime = millisecondsEnd - millisecondsBegin
            self.totalTime += useTime
            resMap = json.loads(res).get("msg")
            self.result.append("请求次数： {} 本次请求结果：{} 用时：{}".format(i, resMap, useTime))
            print(resMap)
        # 释放锁
        semaphore.release()
        print("发送消息给用户 结束处理 {} 数据".format(desc))

    def getSupplierTransferInfo(self):
        print("开始分析Excel")
        transferMap = {}
        # 获取供应商历史数据
        data = File(path=self.param).read_excl()
        for i in data:
            transferMap[i.get('gys_id')] = i.get('new_gys_id')
        transferMap= [{"old": 2494, "new":2480, "order_id": 265632}]
        print("开始组装数据")
        sqlUserList = [
            "UPDATE `supplier`.`supplier_order` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_message_notice` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_order_huishou` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_order_operation_log` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_order_test_project` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_order_test_project_detail` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_user_equipment` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_user_instrument_project` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_user_project_file_record` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_user_settle_project` SET `user_id` = {} WHERE `user_id` = {};",
            "UPDATE `supplier`.`supplier_user_settle_project_new` SET `user_id` = {} WHERE `user_id` = {};"
        ]

        sqlOrderList = [
            "UPDATE `supplier`.`supplier_order` SET `user_id` = {} WHERE `user_id` = {} and order_id = {};",
            "UPDATE `supplier`.`supplier_message_notice` SET `user_id` = {} WHERE `user_id` = {} and order_id = {};",
            "UPDATE `supplier`.`supplier_order_huishou` SET `user_id` = {} WHERE `user_id` = {} and order_id = {};",
            "UPDATE `supplier`.`supplier_order_operation_log` SET `user_id` = {} WHERE `user_id` = {} and order_id = {};",
            "UPDATE `supplier`.`supplier_order_test_project` SET `user_id` = {} WHERE `user_id` = {} and order_id = {};",
            "UPDATE `supplier`.`supplier_order_test_project_detail` SET `user_id` = {} WHERE `user_id` = {} and order_id = {};",
        ]

        if self.operationType == "order":
            sqlList = sqlOrderList
        else:
            sqlList = sqlUserList

        newSqlList = []
        for i in sqlList:
            if self.operationType == "order":
                for m in transferMap:
                    newSqlList.append(i.format(int(m.get("new")), int(m.get("old")), int(m.get("order_id"))))
            else:
                for k, v in transferMap.items():
                    newSqlList.append(i.format(int(v), int(k)))
        print("开始写入文件")
        File(path=self.path, txtData=newSqlList).writeTxt()
        print("。。。end")

    def getChatMessage(self):

        mdb = Mogo().cursor()
        collection = mdb['room']

        date_threshold = int(datetime(2025, 4, 1).timestamp())
        res = collection.find({"createdAt": {"$gt": date_threshold}},
                              {"_id": 1, "conversationUUID": 1, "name": 1, "createdAt": 1, "userPhone": 1,
                               "sourceUrl": 1})

        tmpList = []
        for r in res:
            tmpList.append(r.get("_id"))
            self.tmpMap[str(r.get("_id"))] = r

        # 分组
        newList = Array(target=tmpList, step=50).ArrayChunk()

        # 启用多携程查询
        MyThreading(num=4, data=newList, func=self.getChatMessages).semaphoreJob()

        excelData = []

        for i in tmpList:
            tmpExcelData = {}
            if self.tmpMap.get(str(i)) is not None:
                seconds = self.tmpMap.get(str(i)).get("createdAt") / 1000.0
                # 转换为标准时间格式
                standard_time = datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')
                tmpExcelData['createdAt'] = standard_time
                tmpExcelData['userPhone'] = self.formatPhone(self.tmpMap.get(str(i)).get("userPhone"))
                tmpExcelData['sourceUrl'] = self.tmpMap.get(str(i)).get("sourceUrl")

                tmpExcelData['chatMessage'] = "\r\n".join(self.chatMap.get(str(i)))

            excelData.append(tmpExcelData)

        File(path="../.././data/chatMessage.xlsx", fileData={0: excelData}, sheetName={0: "聊天记录"},
             sheetTitle={0: ["createdAt", "userPhone", "sourceUrl", "chatMessage"]}).writeExcel()

    def getChatHistoryMessage(self):
        mdb = Mogo().cursor()
        collection = mdb['userRoom']

        date_begin = int(datetime(2025, 4, 1).timestamp()) * 1000
        date_end = int(datetime(2025, 5, 30).timestamp() + 86400) * 1000
        res = collection.find({"$and": [
            {"createdAt": {"$gt": date_begin}},
            {"createdAt": {"$lt": date_end}}
        ]}, {"_id": 1, "roomId": 1, "userId": 1, "communicateTime": 1})

        tmpList = []
        for r in res:
            key = "{}-{}".format(r.get("roomId"), r.get("userId"))
            tmpList.append(key)
            self.tmpMap[key] = r

        # 分组
        newList = Array(target=tmpList, step=50).ArrayChunk()

        # 启用多携程查询
        MyThreading(num=5, data=newList, func=self.getChatHistoryMessages).semaphoreJob()

        excelData = []
        for k, v in self.tmpMap.items():

            phone = self.formatStr(self.chatMap.get(str(k)).get("userInfo", {}).get("phone", ""))
            wxCode = self.formatStr(self.chatMap.get(str(k)).get("userInfo", {}).get("wxCode", ""))
            fixPhone = self.formatStr(self.chatMap.get(str(k)).get("userInfo", {}).get("fixPhone", ""))
            QQCode = self.formatStr(self.chatMap.get(str(k)).get("userInfo", {}).get("QQCode", ""))
            email = self.formatStr(self.chatMap.get(str(k)).get("userInfo", {}).get("email", ""))

            cList = []

            if len(phone) != 0:
                cList.append(phone)
            if len(wxCode) != 0:
                cList.append(wxCode)
            if len(fixPhone) != 0:
                cList.append(fixPhone)
            if len(QQCode) != 0:
                cList.append(QQCode)
            if len(email) != 0:
                cList.append(email)

            if len(cList) > 0:
                phoneStatus = "是"
                info = ",".join(cList)
            else:
                info = ""
                phoneStatus = "否"

            for mm in self.chatMap.get(str(k), {}).get("chat", {}):
                excelData.append({
                    "客服姓名": self.chatMap.get(str(k)).get("kfName", ""),
                    "是否留电": phoneStatus,
                    "联系方式": info,
                    "开始时间": mm.get("beginDate", ""),
                    "结束时间": mm.get("endDate", ""),
                    "聊天信息": "\r\n".join(mm.get("message", []))
                })

        File(path="../.././data/chatHistoryMessage.xlsx", fileData={0: excelData}, sheetName={0: "聊天记录"},
             sheetTitle={0: ["客服姓名", "是否留电", "联系方式", "开始时间", "结束时间", "聊天信息"]}).writeExcel()

        print("数据已写入 chatHistoryMessage.xlsx")

    def getChatMessages(self, data, desc, semaphore):
        print("获取聊天室消息 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()

        for i in data:
            mdb = Mogo().cursor()
            collection = mdb['userMessage']
            res = collection.find({"roomId": str(i)}, {"messageType": 1, "userId": 1, "mallUserName": 1, "createdAt": 1,
                                                       "contentText": 1}).sort("createdAt", 1)
            tmpRoom = []
            for n in res:
                if n.get("messageType") == 1000004:
                    continue
                seconds = n.get("createdAt") / 1000.0
                # 转换为标准时间格式
                standard_time = datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')
                tmpRoom.append(
                    "时间：{} {}: {}".format(standard_time, self.useMap(n.get("messageType")), n.get("contentText")))

            self.chatMap[str(i)] = tmpRoom

        # 释放锁
        semaphore.release()
        print("获取聊天室消息 处理结束 {} 数据".format(desc))

    def getChatHistoryMessages(self, data, desc, semaphore):
        print("获取客服历史消息 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        mdb = Mogo().cursor()
        for i in data:
            tmp = i.split("-")
            roomId = tmp[0]
            userId = tmp[1]

            collection = mdb['user']
            res = collection.find({"workNo": str(userId)}, {"userName": 1, "workNo": 1})
            for s in res:
                self.chatMap[i] = {"kfName": s.get("userName")}

            collection = mdb['roomCustomer']
            res2 = collection.find({"roomId": str(roomId)},
                                   {"phone": 1, "wxCode": 1, "fixPhone": 1, "QQCode": 1, "email": 1})
            for s in res2:
                self.chatMap[i]["userInfo"] = s

            timeList = self.tmpMap.get(i).get("communicateTime")

            tmpChatList = []
            for k, v in timeList.items():

                if v.get("start") is None or v.get("end") is None:
                    print("开始时间或结束时间为空 跳过")
                    continue

                tmpChat = {}
                collection1 = mdb['userMessage']
                res1 = collection1.find({"$and": [
                    {"roomId": roomId},
                    {"createdAt": {"$gt": v.get("start")}},
                    {"createdAt": {"$lt": v.get("end")}}
                ]}, {"messageType": 1, "userId": 1, "mallUserName": 1, "createdAt": 1,
                     "contentText": 1}).sort("createdAt", 1)
                tmpRoom = []
                for n in res1:
                    seconds = n.get("createdAt") / 1000.0
                    # 转换为标准时间格式
                    standard_time = datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')
                    tmpRoom.append(
                        "时间：{} {}: {}".format(standard_time, self.useMap(n.get("messageType")), n.get("contentText")))

                tmpChat["beginDate"] = datetime.fromtimestamp(v.get("start") / 1000).strftime('%Y-%m-%d %H:%M:%S')
                tmpChat["endDate"] = datetime.fromtimestamp(v.get("end") / 1000).strftime(
                    '%Y-%m-%d %H:%M:%S')
                tmpChat["message"] = tmpRoom
                tmpChatList.append(tmpChat)
            self.chatMap[i]["chat"] = tmpChatList

        # 释放锁
        semaphore.release()
        print("获取客服历史消息 处理结束 {} 数据".format(desc))

    def getChatHistoryStatistics(self, data, desc, semaphore):
        print("补充历史聊天数据 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        mdb = Mogo(db="fdfdMogoPro").cursor()
        for i in data:
            tmp = i.split("-")
            roomId = tmp[0]

            # 获取客户手动保存的消息
            collection = mdb['roomCustomer']
            res2 = collection.find_one({"roomId": str(roomId)},
                                       {"phone": 1, "sampleName": 1, "itemName": 1, "userType": 1, "remark": 1,
                                        "wxFileUrl": 1, "wxCode": 1, "fixPhone": 1, "QQCode": 1, "email": 1})
            userInfo = {}
            for s in res2:
                userInfo = s

            # 获取客户手动保存的消息
            collection = mdb['room']
            res3 = collection.find({"_id": str(roomId)},
                                   {"baiduSource": 1, "baiduKeyword": 1})
            roomInfo = {}
            for x in res3:
                roomInfo = x

            timeList = self.tmpMap.get(i).get("communicateTime")

            tmpChatList = []
            for k, v in timeList.items():

                if v.get("start") is None or v.get("end") is None:
                    print("开始时间或结束时间为空 跳过")
                    continue

                tmpChat = {}
                collection1 = mdb['userMessage']
                res1 = collection1.find({"$and": [
                    {"roomId": roomId},
                    {"createdAt": {"$gt": v.get("start")}},
                    {"createdAt": {"$lt": v.get("end")}},
                    {"messageType": {"$in": [1000001, 1000003]}}
                ]}, {"messageType": 1, "userId": 1, "mallUserName": 1, "createdAt": 1,
                     "contentText": 1}).sort("createdAt", 1)

                userNum = 0
                serviceNum = 0

                for n in res1:
                    if n.get("messageType") == 1000001:
                        if n.get("contentText") != "转人工":
                            userNum += 1
                    else:
                        serviceNum += 1
                tmpChat["start"] = v.get("start")
                tmpChat["end"] = v.get("end")
                tmpChat["userNum"] = userNum
                tmpChat["serviceNum"] = serviceNum
                tmpChatList.append(tmpChat)

            self.chatMap[i] = {
                'userInfo': userInfo,
                'room': roomInfo,
                'chat': tmpChatList
            }

        # 释放锁
        semaphore.release()
        print("补充历史聊天数据 处理结束 {} 数据".format(desc))

    @staticmethod
    def useMap(identify):
        targetMap = {
            1000004: "系统",
            1000001: "商城客户",
            1000002: "AI",
            1000003: "客服"
        }

        return targetMap.get(identify)

    @staticmethod
    def formatPhone(phone):
        if phone is None or len(phone) == 0:
            return ""
        else:
            phone_number = str(phone)
            # 检查手机号码长度是否符合要求
            if len(phone_number) != 11:
                return ""

            # 隐藏中间四位
            return phone_number[:3] + "****" + phone_number[7:]

    @staticmethod
    def formatStr(text):
        if text is None or len(text) == 0:
            return ""
        else:
            length = len(text)
            if length < 4:
                return text  # 长度不足4时返回原字符串
            start = (length - 4) // 2
            return text[:start] + '****' + text[start + 4:]

    def testMultithreading(self):
        newList = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        # 启用多携程查询
        MyThreading(num=10, data=newList, func=self.dealMultithreading).semaphoreJob()

        # import redis
        #
        # r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        #
        # lua_script = """
        # local json_data = redis.call('GET', KEYS[1])
        # if not json_data then
        #     return false
        # end
        # if json_data == "1" or json_data == "2" then
        #     return false
        # else
        #     local ok, redis_data = pcall(cjson.decode, json_data)
        #     if not ok then
        #         return false
        #     end
        #     if redis_data["sync_deal"] == 0 then
        #         redis.call('SET', KEYS[2], ARGV[1])
        #         return cjson.encode(redis_data)  -- 返回序列化数据
        #     else
        #         return false
        #     end
        # end
        # """
        #
        # result = r.eval(
        #     lua_script,
        #     2,  # 键的数量
        #     '123456',  # KEYS[1]
        #     '123456',  # KEYS[2]
        #     '121212'  # ARGV[1]（原ARGV[2]未使用，可移除）
        # )
        #
        # print(result)  # 输出反序列化后的字典

    def dealMultithreading(self, data, desc, semaphore):
        # print("测试多线程 开始处理 {} 数据".format(desc))
        # 上锁
        semaphore.acquire()
        for i in data:
            millisecondsBegin = time.time_ns() // 1_000_000
            res = Curl(url="http://api.test.oa.sci-go.com/oa/api/deal-audit",
                       param=json.dumps(self.param)).panGuSkuStatus()
            millisecondsEnd = time.time_ns() // 1_000_000
            useTime = millisecondsEnd - millisecondsBegin
            self.totalTime += useTime
            resMap = json.loads(res).get("msg")
            self.result.append("请求次数： {} 本次请求结果：{} 用时：{}".format(i, resMap, useTime))
            print(resMap)
        # 释放锁
        semaphore.release()
        # print("测试多线程 结束处理 {} 数据".format(desc))

    def compareSupplier(self):
        # 读取供应商系统配置数据
        supplierSystemList = File(path=self.param).read_excl()
        # 读取供应商后台配置数据
        supplierBack = File(path=self.path).read_excl()

        supplierBackMap = {}

        for i in supplierBack:
            payType = i.get("pay_type")

            if math.isnan(payType):
                continue
            if i.get("pay_type") == 110006001:
                payType = 1
            elif i.get("pay_type") == 110006002:
                payType = 2
            elif i.get("pay_type") == 110006003:
                payType = 3
            elif i.get("pay_type") == 110006004:
                payType = 4

            i['pay_type'] = payType

            supplierBackMap[i.get("gys_history_id")] = i

        supplierBackLose = []
        supplierSystemDiff = []

        for i in supplierSystemList:
            if supplierBackMap.get(i.get("id")) is not None:
                if i.get("payment_methods") != supplierBackMap.get(i.get("id")).get("pay_type"):
                    supplierSystemDiff.append({"supplier_id": i.get("id"),
                                               "sys_pay": i.get("payment_methods"),
                                               "sys_alipay_name": i.get("alipay_name"),
                                               "sys_alipay_account": i.get("alipay_account"),
                                               "sys_qr_code": i.get("qr_code"),
                                               "back_pay": supplierBackMap.get(i.get("id")).get("pay_type"),
                                               "back_payee_name": supplierBackMap.get(i.get("id")).get("payee_name"),
                                               "back_payee_account": supplierBackMap.get(i.get("id")).get(
                                                   "payee_account"),
                                               "back_payee_code_url": supplierBackMap.get(i.get("id")).get(
                                                   "payee_code_url")})
            else:
                supplierBackLose.append({"supplier_id": i.get("id"), "payment_methods": i.get("payment_methods")})

        updatePayMethodList = []

        print("供应商系统差异付款方式")
        print(len(supplierSystemDiff))
        for i in supplierSystemDiff:
            if i.get("back_pay") == 2:
                sql = " UPDATE supplier.supplier_user_base SET payment_methods = 2"
                if i.get("sys_alipay_name") != i.get("back_payee_name"):
                    sql = sql + ", alipay_name = '{}' ".format(i.get("back_payee_name"))
                if i.get("sys_alipay_account") != i.get("back_payee_account"):
                    sql = sql + ", alipay_account = '{}' ".format(i.get("back_payee_account"))

                sql = sql + " WHERE id = {}; ".format(i.get("supplier_id"))
                updatePayMethodList.append(sql)
            elif i.get("back_pay") == 3:
                sql = " UPDATE supplier.supplier_user_base SET payment_methods = 3"
                if i.get("sys_qr_code") != i.get("back_payee_code_url"):
                    if math.isnan(i.get("back_payee_code_url")) is False:
                        sql = sql + ", qr_code = '{}' ".format(i.get("back_payee_code_url"))
                sql = sql + " WHERE id = {}; ".format(i.get("supplier_id"))
                updatePayMethodList.append(sql)
            elif i.get("back_pay") == 4:
                sql = " UPDATE supplier.supplier_user_base SET payment_methods = 4"
                if i.get("sys_qr_code") != i.get("back_payee_code_url"):
                    if math.isnan(i.get("back_payee_code_url")) is False:
                        sql = sql + ", qr_code = '{}' ".format(i.get("back_payee_code_url"))
                sql = sql + " WHERE id = {}; ".format(i.get("supplier_id"))
                updatePayMethodList.append(sql)

        print("供应商后台缺失供应商配置")
        print(len(supplierBackLose))

        for i in updatePayMethodList:
            print(i)

    def findData(self):
        mdb = Mogo(db="fdfdMogoPro").cursor()
        collection = mdb['roomCustomer']

        res = collection.find({}, {"_id": 1, "userUUID": 1, "roomId": 1})

        deleteId = []
        num = 0
        for i in res:
            if len(i.get("roomId", "")) == 0:
                deleteId.append(i.get("_id"))
                num = num + 1

        print("本次需要删除的数据有" + str(num) + "条")

        tmpList = Array(target=deleteId, step=10).ArrayChunk()

        deleteNum = 0
        for i in tmpList:
            result = collection.delete_many({"_id": {"$in": i}})
            print("当前已删除：" + result.deleted_count + "条")
            deleteNum += result.deleted_count

        print(f"成功删除了 {deleteNum} 条数据")

    def fixHistoryChatStatistics(self):
        mdb = Mogo(db="fdfdMogoPro").cursor()
        collection = mdb['userRoom']

        date_begin = int(datetime(2025, 4, 1).timestamp()) * 1000
        date_end = int(datetime(2025, 5, 30).timestamp() + 86400) * 1000
        res = collection.find({"$and": [
            {"createdAt": {"$gt": date_begin}},
            {"createdAt": {"$lt": date_end}}
        ]}, {"_id": 1, "roomId": 1, "userId": 1, "communicateTime": 1})

        for r in res:
            key = "{}-{}".format(r.get("roomId"), r.get("userId"))
            self.tmpMap[key] = r

        # 分组
        newList = Array(target=list(self.tmpMap.keys()), step=50).ArrayChunk()

        # 启用多携程查询
        MyThreading(num=5, data=newList, func=self.getChatHistoryStatistics).semaphoreJob()

        saveList = []
        for k, v in self.tmpMap.items():
            phone = self.chatMap.get(str(k)).get("saveInfo", {}).get("phone", "")
            wxCode = self.chatMap.get(str(k)).get("saveInfo", {}).get("wxCode", "")
            fixPhone = self.chatMap.get(str(k)).get("saveInfo", {}).get("fixPhone", "")
            QQCode = self.chatMap.get(str(k)).get("saveInfo", {}).get("QQCode", "")
            email = self.chatMap.get(str(k)).get("saveInfo", {}).get("email", "")
            userType = self.chatMap.get(str(k)).get("saveInfo", {}).get("userType", 0)
            project = self.chatMap.get(str(k)).get("saveInfo", {}).get("itemName", "")
            sampleName = self.chatMap.get(str(k)).get("saveInfo", {}).get("sampleName", "")
            remark = self.chatMap.get(str(k)).get("saveInfo", {}).get("remark", "")
            wxFileUrl = self.chatMap.get(str(k)).get("saveInfo", {}).get("wxFileUrl", "")
            firstReception = v.get("userId")
            lastReception = v.get("userId")
            source = self.chatMap.get(str(k)).get("room", {}).get("baiduSource", "")
            keyWord = self.chatMap.get(str(k)).get("room", {}).get("baiduKeyword", "")

            for n in self.chatMap.get(str(k)).get("chat"):
                saveList.append(
                    {
                        "visitAt": int(n.get("start") / 1000.0),
                        "dialogueSAt": int(n.get("start") / 1000.0),
                        "dialogueEAt": int(n.get("end") / 1000.0),
                        "source": source,
                        "mobile": phone,
                        "roomId": str(v.get("roomId")),
                        "sampleName": sampleName,
                        "project": project,
                        "userType": userType,
                        "wechatCode": wxCode,
                        "wechatQr": wxFileUrl,
                        "telephone": fixPhone,
                        "QQCode": QQCode,
                        "email": email,
                        "remark": remark,
                        "keyWord": keyWord,
                        "conversationLength": round((n.get("end") / 1000.0 - n.get("start") / 1000.0) / 60, 2),
                        "userNum": n.get("userNum", 0),
                        "engineerNum": n.get("serviceNum", 0),
                        "createdAt": int(n.get("start") / 1000.0),
                        "firstReception": firstReception,
                        "lastReception": lastReception,
                    }
                )

        print("开始写入数据")
        mdb = Mogo(db="fdfdMogoPro").cursor()
        collection = mdb['userChatStatistics']

        collection.insert_many(saveList)

        print("数据写入完成")

    def findRoom(self):
        mdb = Mogo(db="fdfdMogoPro").cursor()
        collection = mdb['room']

        res = collection.find({}, {"_id": 1, "conversationUUID": 1})

        uniqMap = {}
        resMap = {}
        unUniqList = []

        for i in res:
            if uniqMap.get(i.get("conversationUUID")) is None:
                uniqMap[i.get("conversationUUID")] = 1
                resMap[i.get("conversationUUID")] = [str(i.get("_id"))]
            else:
                resMap[i.get("conversationUUID")].append(str(i.get("_id")))
                unUniqList.append(i.get("conversationUUID"))

        deleteList = []
        for i in unUniqList:
            num = 0
            for n in resMap[i]:
                if num == 0:
                    num += 1
                    continue
                else:
                    deleteList.append(n)

        if len(deleteList) == 0:
            print("暂无需要删除的数据")
            exit()

        # print(","deleteList)

        # collection = mdb['room']
        # result = collection.delete_many({"_id": {"$in": deleteList}})
        # print("当前已删除：" + result.deleted_count + "条")

    def fixData(self):
        mdb = Mogo(db="fdfdMogoPro").cursor()
        collection = mdb['userChatStatistics']
        res = collection.find({}, {"_id": 1, "roomId": 1})
        num = 0

        for i in res:
            collection = mdb['roomCustomer']
            res2 = collection.find_one({"roomId": i.get("roomId")},
                                       {"phone": 1, "sampleName": 1, "itemName": 1, "userType": 1, "remark": 1,
                                        "wxFileUrl": 1, "wxCode": 1, "fixPhone": 1, "QQCode": 1, "email": 1})
            if res2 is None:
                continue
            mdb = Mogo(db="fdfdMogoPro").cursor()
            collection = mdb['userChatStatistics']
            result = collection.update_one(
                {"_id": i.get("_id")},  # 查询条件
                {"$set": {"mobile": res2.get("phone", ""), "sampleName": res2.get("sampleName", ""),
                          "project": res2.get("itemName", ""), "userType": res2.get("userType", 0),
                          "remark": res2.get("remark", ""),
                          "wechatQr": res2.get("wxFileUrl", ""), "wechatCode": res2.get("wxCode", ""),
                          "telephone": res2.get("fixPhone", ""), "QQCode": res2.get("QQCode", ""),
                          "email": res2.get("email", "")}}  # 更新操作
            )
            num += 1
            print(num)

    def fixData1(self):
        mdb = Mogo(db="fdfdMogoPro").cursor()
        collection = mdb['userChatStatistics']
        res = collection.find({"visitAt": {"$gt": 1748265397}}, {"_id": 1, "roomId": 1, "visitAt": 1})
        num = 0
        mdb = Mogo(db="fdfdMogoPro").cursor()
        for i in res:
            num += 1

            tmpTime = math.ceil(i.get("visitAt") / 1000)

    
            if res is None:
                continue
            collection = mdb['userChatStatistics']

            result = collection.update_one(
                {"_id": i.get("_id")},  # 查询条件
                {"$set": {"visitAt": tmpTime}}  # 更新操作
            )

        print(num)

        # num = 0
        #
        # for i in res:
        #     collection = mdb['roomCustomer']
        #     res2 = collection.find_one({"roomId": i.get("roomId")},
        #                                {"phone": 1, "sampleName": 1, "itemName": 1, "userType": 1, "remark": 1,
        #                                 "wxFileUrl": 1, "wxCode": 1, "fixPhone": 1, "QQCode": 1, "email": 1})
