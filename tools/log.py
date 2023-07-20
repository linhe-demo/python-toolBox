# 日志记录类
import socket

from common.typeEnum import TypeEnum
from model.tencent import Tencent
from pkg.db import Db
from datetime import datetime


class Log:
    def __init__(self, operationType=None):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.action = operationType
        self.actionUser = "python"
        self.date = datetime.now()

    def watchDog(self):
        sql = Tencent(TypeEnum.OPERATION_LOG.value).getSql()
        Db(sql, (self.ip, self.action, self.actionUser, self.date)).execute()

