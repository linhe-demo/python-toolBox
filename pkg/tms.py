import json

from tools.curl import Curl
from tools.log import Log


class Tms:
    def __init__(self, url1=None, url2=None, param=None, dataList=None, orderType=None):
        self.param = param
        self.url1 = url1
        self.url2 = url2
        self.dataList = dataList
        self.orderType = orderType

    def createOrder(self):
        backInfo = ""
        if len(self.dataList) > 0:
            for i in self.dataList:
                if self.orderType == "inbound":
                    backInfo = Curl(url=self.url2,
                                    param=json.dumps({"shipping_plan_id": i})).getPostmanPostRes()
                elif self.orderType == "outbound":
                    backInfo = Curl(url=self.url2,
                                    param=json.dumps({"last_mile_order_sn": i})).getPostmanPostRes()
        else:
            res = Curl(url=self.url1, param=self.param).getPostmanPostRes()
            tmpInfo = json.loads(res)
            Log(level="INFO", text=tmpInfo, console=False).localFile()
            if tmpInfo.get('code', 0) == 20000 and tmpInfo.get('message', '') == 'SUCCESS':
                data = tmpInfo.get('data')
                if self.orderType == "inbound":
                    if len(data.get('shipping_plan_id', '')) == 0:
                        return res
                    else:
                        backInfo = Curl(url=self.url2,
                                        param=json.dumps(
                                            {"shipping_plan_id": data.get("shipping_plan_id")})).getPostmanPostRes()
                elif self.orderType == "outbound":
                    if len(data.get('wms_order_sn', '')) == 0:
                        return res
                    else:
                        backInfo = Curl(url=self.url2,
                                        param=json.dumps(
                                            {"last_mile_order_sn": data.get("wms_order_sn")})).getPostmanPostRes()
        if len(backInfo) > 0:
            Log(level="INFO", text=json.loads(backInfo), console=False).localFile()
        return backInfo
