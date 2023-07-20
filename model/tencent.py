# 腾讯云数据库操作类

class Tencent:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "operationLog": '''
                INSERT INTO user_log (ip, action, action_user, create_time) VALUES ('%s', '%s', '%s', '%s')
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
