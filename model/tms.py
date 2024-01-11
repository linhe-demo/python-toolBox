class TmsTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getTmsInventoryNum": "SELECT warehouse_id, uniq_sku as sku, warehouse_storage as num FROM ffpost_wms.fw_warehouse_storage WHERE uniq_sku IN ('%s')",
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
