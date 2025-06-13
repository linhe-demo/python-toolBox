class FdfdTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getWorkDay": "select * from oa_work_day where year = '%s'",
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
