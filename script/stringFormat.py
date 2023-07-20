import os
import sys

if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from pkg.window import *
    from common.typeEnum import TypeEnum
    from pkg.callBack import CallBack

    window = Window(title="字符串格式化插件", label1="原始数据：", btn1="格式化", btn2="重 置", radio=True,
                    resultName="处理结果：", toolType=TypeEnum.STR_FORMAT.value, callback=CallBack().assembleString)
    window.initWindow()
