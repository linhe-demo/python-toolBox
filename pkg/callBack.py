# 回调函数类
import base64
import json

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

    @staticmethod
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
            if dataList.isJson(dataList) is False or dataList.startswith("{") is False or dataList.endswith("}") is False:
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

    @staticmethod
    def isJson(text):
        try:
            json.loads(text)
            return True
        except ValueError as e:
            return False

    @staticmethod
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

        return textA.strFormat(differA), textA.strFormat(differB)

    @staticmethod
    def strFormat(data):
        tmpStr = ""
        for i in data:
            tmpStr += "{}：{}{}".format(i.get("line", ''), i.get("data", ''), "\n")
        return tmpStr
