# 日志记录类
import json
import logging
import socket

from common.typeEnum import TypeEnum
from model.tencent import Tencent
from pkg.db import Db
from datetime import datetime


class Log:
    def __init__(self, operationType=None, level="ERROR", text=None):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.action = operationType
        self.actionUser = "python"
        self.date = datetime.now()
        self.level = level
        self.text = text

    def watchDog(self):
        sql = Tencent(TypeEnum.OPERATION_LOG.value).getSql()
        Db(sql, (self.ip, self.action, self.actionUser, self.date)).execute()

    def localFile(self):
        # 创建一个logger对象
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # 创建一个文件处理器，使用追加模式来打开文件
        handler = logging.FileHandler('../.././log/runtime.log', mode='a', encoding='utf-8')

        # 定义日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # 将处理器添加到logger对象中
        logger.addHandler(handler)

        # 写入日志
        logger.info(self.text)
