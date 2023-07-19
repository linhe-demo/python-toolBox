# curl 请求类
import json

from tools.readFile import read_json_config
import requests


class Curl:
    def __init__(self, img=None):
        self.img = img

    def getOcrSeverData(self):
        config = read_json_config()  # 获取配置信息
        config = config['ocrSever']
        res = requests.post(config['url'], data=json.dumps({"file": self.img, "type": "text", "fileType": 2}),
                            headers={'content-type': 'application/json'})
        return json.loads(res.content)
