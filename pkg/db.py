# 数据库查询类
import pymysql

from tools.file import File


class Db:
    def __init__(self, sql=None, param=None, db=None, showlog=None):
        self.config = self.config()
        self.sql = sql
        self.param = param
        self.db = db
        self.conn = self.connection()
        self.showLog = showlog
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    @staticmethod
    def config():
        dbConfig = File(path="\config\config.json")
        return dbConfig.read_json_config()

    def getCoon(self):
        return self.connection()

    def connection(self):
        if self.db is None:
            tmpConfig = self.config['tencentDb']
        else:
            tmpConfig = self.config[self.db]

        return pymysql.connect(host=tmpConfig['host'], port=tmpConfig['port'], database=tmpConfig['database'],
                               user=tmpConfig['user'],
                               password=tmpConfig['password'], connect_timeout=tmpConfig['timeout'])

    def getAll(self):
        try:
            if self.showLog is True:
                print(self.sql % self.param)

            self.cursor.execute(self.sql % self.param)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return None

    def getOne(self):
        try:
            if self.showLog is True:
                print(self.sql % self.param)
            self.cursor.execute(self.sql % self.param)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error: {e}")
            return None

    def execute(self):
        try:
            if self.showLog is True:
                print(self.sql % self.param)
            if self.param is None:
                self.cursor.execute(self.sql)
            else:
                self.cursor.execute(self.sql % self.param)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e} %s" % format(self.sql % self.param))
            self.conn.rollback()
            return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()
