# 输出类
import json


class Output:
    def __init__(self, code=None, msg=None, data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def send(self):
        return json.dumps({"code": self.code, "msg": self.msg, "data": self.data}, indent=4, ensure_ascii=False,
                          sort_keys=True)
