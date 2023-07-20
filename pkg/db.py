# 数据库查询类
import pymysql

from tools.readFile import File


class Db:
    def __init__(self, sql=None, param=None):
        self.config = self.config()
        self.sql = sql
        self.param = param
        self.conn = self.connection()
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    @staticmethod
    def config():
        dbConfig = File(path="\config\config.json")
        return dbConfig.read_json_config()

    def connection(self):
        tmpConfig = self.config['tencentDb']
        return pymysql.connect(host=tmpConfig['host'], port=tmpConfig['port'], database=tmpConfig['database'],
                               user=tmpConfig['user'],
                               password=tmpConfig['password'], connect_timeout=tmpConfig['timeout'])

    def getAll(self):
        try:
            self.cursor.execute(self.sql % self.param)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return None

    def getOne(self):
        try:
            self.cursor.execute(self.sql % self.param)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error: {e}")
            return None

    def execute(self):
        try:
            self.cursor.execute(self.sql % self.param)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()
