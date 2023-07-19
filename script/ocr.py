import base64
import os
import sys


def analyzePictureTextApi(name):
    f = open(name, 'rb')
    img = base64.b64encode(f.read())
    imgStr = str(img, 'utf-8')
    return Curl(imgStr).getOcrSeverData().get('result')


if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    from tools.curl import Curl
    from pkg.window import *

    window = Window(title="OCR图文识别插件", height=575, label1="上传图片", btn1="文字提取", btn2="重置",
                    resultName="分析结果：", toolType=OCR, callback=analyzePictureTextApi)
    window.initWindow()
