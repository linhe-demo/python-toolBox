from tools.curl import Curl


class Tms:
    def __init__(self, url=None, param=None):
        self.param = param
        self.url = url

    def createOutboundOrder(self):
        return Curl(url=self.url, param=self.param).getPostmanPostRes()
