# curl 请求类
import json

from tools.readFile import File
import requests


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
        res = requests.post(self.url, data=self.param, headers={'content-type': 'application/json'})
        return res.content

    def getPostmanGetRes(self):
        res = requests.get(self.url, data=self.param, headers={'content-type': 'application/json'})
        return res.content
