import json

from tools.curl import Curl


class Tms:
    def __init__(self, url1=None, url2=None, param=None):
        self.param = param
        self.url1 = url1
        self.url2 = url2

    def createOutboundOrder(self):
        res = Curl(url=self.url1, param=self.param).getPostmanPostRes()
        res = json.loads(res)
        if res.get('code', 0) == 20000 and res.get('message', '') == 'SUCCESS':
            data = res.get('data')
            if len(data.get('wms_order_sn', '')) == 0:
                return res
            else:
                return Curl(url=self.url2, param=json.dumps({"last_mile_order_sn": data.get("wms_order_sn")})).getPostmanPostRes()

