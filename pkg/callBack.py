# 回调函数类
import base64

from tools.curl import Curl


class CallBack:
    def __init__(self):
        pass

    @staticmethod
    def analyzePictureTextApi(name):
        f = open(name, 'rb')
        img = base64.b64encode(f.read())
        imgStr = str(img, 'utf-8')
        return Curl(imgStr).getOcrSeverData().get('result')
