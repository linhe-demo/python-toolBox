from pymongo import MongoClient

from tools.file import File


class Mogo:
    def __init__(self, db=None):
        self.db = db
        self.config = self.config()
        self.connect = self.init()


    def init(self):
        if self.db is None:
            self.db = "fdfdMogoTest"
        return MongoClient(
             self.config.get(self.db).get("dsn"), directConnection=True,  # 绕过副本集检测
    serverSelectionTimeoutMS=10000)
    def cursor(self):
        return self.connect['aichat']

    @staticmethod
    def config():
        dbConfig = File(path="\config\config.json")
        return dbConfig.read_json_config()


