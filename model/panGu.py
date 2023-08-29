
class PanGuTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getCloneData": '''
                SELECT origin_sku_id, cloned_sku_id FROM clone_records
            ''',
            "getSkuInfo": '''
                SELECT id, sku FROM product_sku WHERE id in (%s)
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)