import unicodedata
from model.website import websiteTable
from pkg.db import Db
from tools.array import Array
from tools.file import File


class Website:
    def __init__(self, param=None, param2=None, path=None):
        self.param = param
        self.param2 = param2
        self.path = path
        self.resData = []
        self.resData2 = []
        self.target = []

    def colorTranslate(self):
        translateMap = {}
        sql = websiteTable(index="getTmpColor").getSql()
        data = Db(sql=sql, param=(), db="panGuWebPron").getAll()
        for i in data:
            tmpKey = "{}-{}".format(i.get("color").lower(), i.get("languages_id"))
            translateMap[tmpKey] = i.get("value").lower()

        self.fixAttribute(translateMap)
        self.fixStyle(translateMap)

        File(path="../.././data/websiteUpdateColorTranslateSql.txt", txtData=self.resData).writeTxt()
        File(path="../.././data/websiteGuBackupColorTranslateSql.txt", txtData=self.resData2).writeTxt()

    def fixAttribute(self, translateMap):
        print("website attribute language")
        sql = websiteTable(index="getAttributeDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="websiteTest").getAll()

        for i in data:
            tmpKey = "{}-{}".format(i.get("color").lower(), i.get("languages_id"))
            if translateMap.get(tmpKey) is not None:
                if self.remove_accents(translateMap.get(tmpKey)) != self.remove_accents(i.get("value").lower()):
                    self.resData.append(
                        '''update jjshouse.attribute_languages_v2 set attr_values = "{}" where attr_lang_id = {};'''.format(
                            translateMap.get(tmpKey).rstrip(), i.get("attr_lang_id")))
                    self.resData2.append(
                        '''update jjshouse.attribute_languages_v2 set attr_values = "{}" where attr_lang_id = {};'''.format(
                            i.get("value"), i.get("attr_lang_id")))

    def fixStyle(self, translateMap):
        print("website style language")
        sql = websiteTable(index="getStyleDiff").getSql()
        data = Db(sql=sql, param=("','".join(self.param), "','".join(self.param2)), db="websiteTest").getAll()

        for i in data:
            tmpKey = "{}-{}".format(i.get("color").lower(), i.get("languages_id"))
            if translateMap.get(tmpKey) is not None:
                if self.remove_accents(translateMap.get(tmpKey)) != self.remove_accents(i.get("value").lower()):
                    self.resData.append(
                        '''update jjshouse.style_languages set `value` = "{}" where sl_id = {};'''.format(
                            translateMap.get(tmpKey).rstrip(), i.get("sl_id")))
                    self.resData2.append(
                        '''update jjshouse.style_languages set `value` = "{}" where sl_id = {};'''.format(
                            i.get("value"), i.get("sl_id")))

    @staticmethod
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])



