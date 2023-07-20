import os
import sys

if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    from pkg.window import *
    from pkg.callBack import CallBack

    window = Window(title="OCR图文识别插件", height=575, label1="上传图片", btn1="文字提取", btn2="重置",
                    resultName="分析结果：", toolType=TypeEnum.OCR.value, callback=CallBack().analyzePictureTextApi)
    window.initWindow()
