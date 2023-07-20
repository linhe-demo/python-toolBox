import json
import os
import sys


def assembleString(dataList, dataType):
    if len(dataList) == 0:
        return json.dumps({"code": 500, "msg": "error", "data": "请输入需要格式化的内容"}, indent=4, ensure_ascii=False,
                          sort_keys=True)
    if dataType == 1:
        newData = []
        for i in dataList:
            if "\t" in i:
                newData = newData + i.split("\t")
            if ' ' in i:
                newData = newData + i.split(' ')
            else:
                newData.append(i)
        backInfo = ",".join(newData)

    elif dataType == 3:
        if isJson(dataList) is False or dataList.startswith("{") is False or dataList.endswith("}") is False:
            return json.dumps({"code": 500, "msg": "error", "data": "请输入正确的json数据"}, indent=4, ensure_ascii=False,
                              sort_keys=True)
        backInfo = json.dumps(json.loads(dataList), indent=4, ensure_ascii=False).replace(
            '\\n\\tat',
            ' \n ').replace(
            "\\n", ' \n ')
    else:
        newData = []
        for i in dataList:
            if "\t" in i:
                newData = newData + i.split("\t")
            if ' ' in i:
                newData = newData + i.split(' ')
            else:
                newData.append(i)
        backInfo = "','".join(newData)
        backInfo = "'" + backInfo + "'"
    return backInfo


def isJson(text):
    try:
        json.loads(text)
        return True
    except ValueError as e:
        return False


if __name__ == "__main__":
    # 引入自定义包路径

    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from pkg.window import *
    from common.typeEnum import TypeEnum
    window = Window(title="字符串格式化插件", label1="原始数据：", btn1="格式化", btn2="重 置", radio=True,
                    resultName="处理结果：", toolType=TypeEnum.STR_FORMAT.value, callback=assembleString)
    window.initWindow()
