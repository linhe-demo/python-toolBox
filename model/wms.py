class WmsTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getCategoryData": "SELECT * FROM %s WHERE platform_sku like  %s",

            "getInventoryAgeSkuList": "SELECT distinct sku FROM fw_inventory",

            "getInventoryAgeInitData": '''SELECT
	                                             fi.sku,
	                                             sum( fi.available_qty + fi.exp_shelve_qty + fi.occupied_qty + fi.locking_qty + fi.suspense_qty + fi.in_transit_qty ) AS num,
	                                             fi.warehouse_code,
	                                             0 AS inventory_type,
	                                             1 AS `status`,
	                                            ( SELECT IFNULL( max( create_time ), '2023-11-08 00:00:00' ) FROM fw_inventory_log fil WHERE fil.sku = fi.sku AND fil.business_type = 'INBOUND' ) AS create_time 
                                          FROM
	                                            fw_inventory fi 
                                          WHERE
                                                fi.sku IN ('%s')
                                          AND
	                                            `status` IN ( 500, 700, 800 ) 
                                          GROUP BY
	                                            sku
                                          HAVING num > 0'''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)