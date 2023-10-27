class WmsTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getCategoryData": "SELECT * FROM %s WHERE platform_sku like  %s"
        }

    def getSql(self):
        return self.sqlMap().get(self.index)