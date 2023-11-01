import json

from tools.curl import Curl
from tools.log import Log


class Tms:
    def __init__(self, url1=None, url2=None, param=None, dataList=None):
        self.param = param
        self.url1 = url1
        self.url2 = url2
        self.dataList = dataList

    def createOutboundOrder(self):

        backInfo = ""

        if len(self.dataList) > 0:
            for i in self.dataList:
                backInfo = Curl(url=self.url2,
                                param=json.dumps({"last_mile_order_sn": i})).getPostmanPostRes()
        else:
            res = Curl(url=self.url1, param=self.param).getPostmanPostRes()
            info = json.loads(res)
            Log(level="INFO", text=info).localFile()

            if res.get('code', 0) == 20000 and res.get('message', '') == 'SUCCESS':
                data = res.get('data')
                if len(data.get('wms_order_sn', '')) == 0:
                    return res
                else:
                    backInfo = Curl(url=self.url2,
                                    param=json.dumps(
                                        {"last_mile_order_sn": data.get("wms_order_sn")})).getPostmanPostRes()
        Log(level="INFO", text=json.loads(backInfo)).localFile()
        return backInfo
