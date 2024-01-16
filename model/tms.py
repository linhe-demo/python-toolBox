class TmsTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getTmsInventoryNum": '''SELECT warehouse_id, uniq_sku as sku, warehouse_storage as num FROM ffpost_wms.fw_warehouse_storage WHERE uniq_sku IN ('%s');''',
            "getNotShippedOrderBySkuId": '''
                SELECT 
                            fgss.* 
                FROM 
                            fw_goods_shipping fgss 
                INNER JOIN 
                            fw_goods_shipping_detail fgsd ON fgsd.last_mile_order_sn = fgss.last_mile_order_sn 
                INNER JOIN
                            fw_goods_sku fgs ON fgsd.sku_id = fgs.sku_id
                WHERE 
                            fgs.warehouse_sku = '%s' and fgss.order_status in (0,1)
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
