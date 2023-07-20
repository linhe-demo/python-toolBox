import os
import sys

if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from pkg.window import Window
    from common.typeEnum import TypeEnum
    from pkg.callBack import CallBack

    window = Window(title="文本比较工具", label1="需要比较的文本A：", label2="需要比较的文本B：", btn1="比较", btn2="重置",
                    resultName="比对结果：", toolType=TypeEnum.STR_COMPARE.value, callback=CallBack().compareText)
    window.initWindow()
