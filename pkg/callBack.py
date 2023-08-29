# 回调函数类
import base64
import json

from common.errorEnum import ErrorEnum
from common.typeEnum import TypeEnum
from pkg.output import Output
from pkg.syncData import SyncData
from tools.curl import Curl


class CallBack:
    def __init__(self):
        self.method = None

    @staticmethod
    def analyzePictureTextApi(name):
        f = open(name, 'rb')
        img = base64.b64encode(f.read())
        imgStr = str(img, 'utf-8')
        return Curl(imgStr).getOcrSeverData().get('result')

    @staticmethod
    def assembleString(dataList, dataType):
        if len(dataList) == 0:
            return Output(code=ErrorEnum.NOT_EMPTY.value['code'], msg="error",
                          data=ErrorEnum.NOT_EMPTY.value['message']).send()
        if dataType == 1:
            backInfo = ",".join(CallBack.analyseData(dataList))

        elif dataType == 3:
            if CallBack.isJson(dataList) is False or dataList.startswith("{") is False or dataList.endswith(
                    "}") is False:
                return Output(code=ErrorEnum.PARAM_ERROR.value['code'], msg="error",
                              data=ErrorEnum.PARAM_ERROR.value['message']).send()
            backInfo = json.dumps(json.loads(dataList), indent=4, ensure_ascii=False).replace(
                '\\n\\tat',
                ' \n ').replace(
                "\\n", ' \n ')
        else:
            backInfo = "','".join(CallBack.analyseData(dataList))
            backInfo = "'" + backInfo + "'"
        return backInfo

    @staticmethod
    def analyseData(dataList):
        newData = []
        for i in dataList:
            if "\t" in i:
                newData = newData + i.split("\t")
            if ' ' in i:
                newData = newData + i.split(' ')
            else:
                newData.append(i)
        return dataList

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

        return CallBack.strFormat(differA), CallBack.strFormat(differB)

    @staticmethod
    def strFormat(data):
        tmpStr = ""
        for i in data:
            tmpStr += "{}：{}{}".format(i.get("line", ''), i.get("data", ''), "\n")
        return tmpStr

    @staticmethod
    def postman(url, param, requestType):
        if url is None or len(url) == 0:
            return Output(code=ErrorEnum.REQUEST_URL_EMPTY.value['code'], msg="error",
                          data=ErrorEnum.REQUEST_URL_EMPTY.value['message']).send()

        curl = Curl(url=url, param=param)

        if requestType.get() == TypeEnum.POST.value:
            info = curl.getPostmanPostRes()
            if CallBack.isJson(info) is True:
                return True, json.dumps(json.loads(info), indent=4, ensure_ascii=False)
            else:
                return False, info
        else:
            info = curl.getPostmanGetRes()
            if CallBack.isJson(info) is True:
                return True, json.dumps(json.loads(info), indent=4, ensure_ascii=False)
            else:
                return False, info

    @staticmethod
    def syncTable(database, condition, index):
        condition_json = json.loads(condition)

        res = SyncData(database=database, table=condition_json.get("table"), condition=condition_json.get("condition")).run()

        return False, res
