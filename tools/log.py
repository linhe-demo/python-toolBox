# 日志记录类
import os
import socket
from datetime import datetime

from loguru import logger

from common.typeEnum import TypeEnum
from model.tencent import Tencent



class Log:
    def __init__(self, operationType=None, level="ERROR", text=None, console=True):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.action = operationType
        self.actionUser = "python"
        self.date = datetime.now()
        self.level = level
        self.text = text
        self.console = console

    def watchDog(self):
        pass
        # sql = Tencent(TypeEnum.OPERATION_LOG.value).getSql()
        # Db(sql, (self.ip, self.action, self.actionUser, self.date)).execute()

    def localFile(self):
        logDir = os.path.expanduser('../.././log')  # expanduser函数，它可以将参数中开头部分的 ~ 或 ~user 替换为当前用户的home目录并返回
        # 按照时间命名
        logFile = os.path.join(logDir, 'runtime.log')
        if not os.path.exists(logDir):
            os.mkdir(logDir)

        if self.console is False:
            logger.remove(handler_id=None)

        logger.add(logFile)
        if self.level == "ERROR":
            logger.error(self.text)
        elif self.level == "INFO":
            logger.info(self.text)
        elif self.level == "SUCCESS":
            logger.success(self.text)
        elif self.level == "WARNING":
            logger.warning(self.text)
