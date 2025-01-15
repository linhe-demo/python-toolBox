# curl 请求类
import hashlib
import json
import math
import time

import requests

from tools.file import File
from tools.log import Log


class Curl:
    def __init__(self, img=None, url=None, param=None, method=None, timestamp=None):
        self.img = img
        self.url = url
        self.param = param
        self.config = File(path="\config\config.json").read_json_config()
        self.method = method
        self.timestamp = timestamp

    def getOcrSeverData(self):
        config = self.config['ocrSever']
        res = requests.post(config['url'], data=json.dumps({"file": self.img, "type": "text", "fileType": 2}),
                            headers={'content-type': 'application/json'})
        return json.loads(res.content)

    def getErpStockInfo(self):
        # 生产函数签名
        sign = self.signFunc()

        Log(level="INFO",
            text="请求地址：{}{}?sign={}&time={} 参数：{}".format(self.config['erp_config']['url'], self.method, sign,
                                                          self.timestamp, self.param)).localFile()
        res = requests.post(
            "{}{}?sign={}&time={}".format(self.config['erp_config']['url'], self.method, sign, self.timestamp),
            data=self.param, json=True)

        # Log(level="INFO", text="返回结果：{}".format(res.content)).localFile()

        if len(res.content) == 0:
            Log(level="INFO", console="接口 {} 未返回数据".format(res.content), text="接口 {} 未返回数据".format(res)).localFile()

        res = json.loads(res.content)
        if res.get('code') != 0:
            Log(level="ERROR", console="接口数据返回异常", text=res.content).localFile()
        else:
            return res

    def getPostmanPostRes(self):
        try:
            Log(level="INFO", text=json.dumps({"url": self.url, "param": json.loads(self.param)}),
                console=False).localFile()
            res = requests.post(self.url, data=self.param, headers={'content-type': 'application/json'})
        except Exception as e:
            return "请求发生错误: {}".format(e)
        if res.content is None:
            return "接口返回数据为空！"
        elif res.content == "":
            return "接口返回空字符串！"
        elif res.content is False:
            return "响应结束！"
        elif res.content == b'':
            return "响应结束！"

        return res.content

    def syncStockInfo(self):
        try:
            res = requests.post(self.url, data=self.param, headers={'token': 'A0E7C4DD3F825B4E571A9F3AFD66AB98AAAAHUYNDAFASWDXFSDFSDGSFDDIUGBKJFDSOBJHA'})
        except Exception as e:
            return "请求发生错误: {}".format(e)
        if res.content is None:
            return "接口返回数据为空！"
        elif res.content == "":
            return "接口返回空字符串！"
        elif res.content is False:
            return "响应结束！"
        elif res.content == b'':
            return "响应结束！"
        return res.content

    def getPostmanGetRes(self):
        try:
            res = requests.get(self.url, data=self.param, headers={'content-type': 'application/json'})
        except Exception as e:
            return "请求发生错误: {}".format(e)
        if res.content is None:
            return "接口返回数据为空！"
        elif res.content == "":
            return "接口返回空字符串！"
        elif res.content is False:
            return "响应结束！"
        elif res.content == b'':
            return "响应结束！"
        return res.content

    def panGuSkuStatus(self):
        try:
            res = requests.post(self.url, data=self.param, headers={'content-type': 'application/json','Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9wYW5ndS5zbWFsb28uY29tXC9hcGlcL2F1dGhvcml6YXRpb25zIiwiaWF0IjoxNzM0MzE0MTYxLCJleHAiOjE3MzQ0MDA1NjEsIm5iZiI6MTczNDMxNDE2MSwianRpIjoiRkJjYkxOWHpFdkdYMDU2WiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyJ9.mjYR3nEmDYVrVa64TxRVjO_DOEG_WWdZJw7idzASEu4'})
        except Exception as e:
            return "请求发生错误: {}".format(e)
        if res.content is None:
            return "接口返回数据为空！"
        elif res.content == "":
            return "接口返回空字符串！"
        elif res.content is False:
            return "响应结束！"
        elif res.content == b'':
            return "响应结束！"
        return res.content

    def signFunc(self):
        newParam = sorted(self.param.items(), key=lambda x: x[0])
        newDict = {}
        for k, v in newParam:
            newDict[k] = v
        tmpStr = str(json.dumps(newDict, separators=(',', ':')))

        tmpSignStr = "{}{}".format(tmpStr, self.config['erp_config']['appSecret'])

        m = hashlib.sha1()
        m.update(tmpSignStr.encode('utf-8'))

        return "{}.{}".format(self.config['erp_config']['appId'], m.hexdigest())
