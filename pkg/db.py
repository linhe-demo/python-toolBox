# 数据库连接类
import pymysql

from tools.readFile import read_json_config


class Db:
    def __init__(self):
        self.config = read_json_config()

    @staticmethod
    def connection():
        config = read_json_config()
        tmpConfig = config['db']
        return pymysql.connect(host=tmpConfig['host'], port=tmpConfig['port'], database=tmpConfig['database'],
                               user=tmpConfig['user'],
                               password=tmpConfig['password'], connect_timeout=tmpConfig['timeout'])


        def getAll(sql, param, dbType=None):
            if dbType == 'test':
                db = dbConnection(dbType=dbType)
            else:
                db = dbConnection()

            with db.cursor(cursor=pymysql.cursors.DictCursor) as conn:
                conn.execute(sql % param)
                res = conn.fetchall()
            return res

        def getOne(sql, param):
            db = dbConnection()
            cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute(sql % param)
            return cursor.fetchone()
