# curl 请求类
import json

import requests

from tools.file import File


class Curl:
    def __init__(self, img=None, url=None, param=None):
        self.img = img
        self.url = url
        self.param = param
        self.config = File(path="\config\config.json").read_json_config()

    def getOcrSeverData(self):
        config = self.config['ocrSever']
        res = requests.post(config['url'], data=json.dumps({"file": self.img, "type": "text", "fileType": 2}),
                            headers={'content-type': 'application/json'})
        return json.loads(res.content)

    def getPostmanPostRes(self):
        try:
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

