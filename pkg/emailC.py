import json
import os
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from tools.file import File
from tools.log import Log


class Email:
    def __init__(self, title=None, content=None, receiver=None, fileName=None, filePath=None, deleteStatus=False):
        self.config = self.config()
        self.title = title
        self.content = content
        self.receiver = receiver
        self.fileName = fileName
        self.filePath = filePath
        self.deleteStatus = deleteStatus

    @staticmethod
    def config():
        dbConfig = File(path="\config\config.json")
        return dbConfig.read_json_config()

    def sendEmail(self):
        # 获取邮箱配置信息
        config = self.config['email']
        message = MIMEMultipart()
        message['From'] = "{}".format(config['fromAddress'])
        message['To'] = ",".join(self.receiver)
        message['Subject'] = self.title  # 邮件主题
        message.attach(MIMEText(self.content, 'plain', 'utf-8'))  # 内容, 格式, 编码
        if self.filePath is not None:
            file = MIMEText(open(self.filePath, 'rb').read(), 'base64', 'utf-8')
            file["Content-Type"] = 'application/octet-stream'
            file["Content-Disposition"] = 'attachment; filename="%s"' % self.fileName
            message.attach(file)
        try:
            mailers = smtplib.SMTP_SSL(config['host'], config['port'])  # 启用SSL发信, 端口一般是465
            print(mailers)
            mailers.login(config['user'], config['password'])  # 登录验证
            mailers.sendmail(config['fromAddress'], self.receiver, message.as_string())  # 发送
            mailers.quit()
            Log(level="SUCCESS", text="邮件发送成功 {} 收件人：{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.receiver), console=False).localFile()
            if self.deleteStatus is True:
                if os.path.exists(self.filePath):
                    os.remove(self.filePath)
                    Log(level="SUCCESS",
                        text="删除文件成功",
                        console=False).localFile()
                else:
                    Log(level="ERROR",
                        text="删除文件失败",
                        console=False).localFile()
        except smtplib.SMTPException as e:

            Log(level="ERROR",
                text=e,
                console=False).localFile()
