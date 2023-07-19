import os
import sys
from tkinter import *


def compareText(textA, textB):
    tmpList1 = textA.splitlines()
    tmpList2 = textB.splitlines()
    tmpLengthA = len(tmpList1)
    tmpLengthB = len(tmpList2)
    differA, differB = [], []
    if tmpLengthA > tmpLengthB:
        tmpLength = tmpLengthA
    else:
        tmpLength = tmpLengthB

    for i in range(0, tmpLength):
        if tmpLengthA > i:
            tmpTextA = tmpList1[i]
        else:
            tmpTextA = ""

        if tmpLengthB > i:
            tmpTextB = tmpList2[i]
        else:
            tmpTextB = ""
        if tmpTextA != tmpTextB:
            differA.append({"line": i + 1, "data": tmpTextA})
            differB.append({"line": i + 1, "data": tmpTextB})

    return strFormat(differA), strFormat(differB)


def strFormat(data):
    tmpStr = ""
    for i in data:
        tmpStr += "{}：{}{}".format(i.get("line", ''), i.get("data", ''), "\n")
    return tmpStr


if __name__ == "__main__":
    # 引入自定义包路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from pkg.window import Window, STR_COMPARE

    window = Window(title="文本比较工具", label1="需要比较的文本A：", label2="需要比较的文本B：", btn1="比较", btn2="重置",
                    resultName="比对结果：", toolType=STR_COMPARE, callback=compareText)
    window.initWindow()
