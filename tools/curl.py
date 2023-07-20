# curl 请求类
import json

from tools.readFile import File
import requests


class Curl:
    def __init__(self, img=None):
        self.img = img
        self.config = File(path="\config\config.json").read_json_config()

    def getOcrSeverData(self):
        config = self.config['ocrSever']
        res = requests.post(config['url'], data=json.dumps({"file": self.img, "type": "text", "fileType": 2}),
                            headers={'content-type': 'application/json'})
        return json.loads(res.content)
