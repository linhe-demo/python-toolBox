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
	                                            `status` IN ( 200, 500, 700, 800 ) 
                                          GROUP BY
	                                            sku
                                          HAVING num > 0''',
            "getMovePsku": '''
                SELECT 
                            mdt.id, mdt.psku, mdt.location_code, SUM(mdt.available_qty) total, fgs.sku, fgs.sku_id
                FROM 
                            move_de_tmp2 mdt
                INNER JOIN 
                            fw_goods_sku fgs ON fgs.platform_sku = mdt.psku 
                WHERE 1
                ANd mdt.psku NOT IN ('%s')
                AND fgs.warehouse_id = %s
                GROUP BY mdt.psku, mdt.location_code
                HAVING total = 1;
            ''',
            "getNewInventory": '''
                SELECT * FROM fw_inventory where sku = '%s' AND location_code = '%s';
            ''',
            "insertInventoryLog": '''INSERT INTO ff_wms.fw_inventory_log (id,inventory_id,sku,warehouse_code,location_code,platform_code, container_code, po_no,status,sales_status,quality,business_type,business_no,business_code,from_available_qty,to_available_qty,from_exp_shelve_qty,to_exp_shelve_qty,from_locking_qty,to_locking_qty,from_occupied_qty,to_occupied_qty,from_suspense_qty,to_suspense_qty,from_in_transit_qty,to_in_transit_qty,create_time,created_by,update_time,updated_by) VALUES({},{},'{}','{}','{}','{}','{}','{}',{},{},'{}','{}','{}',{},{},{},{},{},{},{},{},{},{},{},{},{},'{}','{}','{}','{}');''',
            "insertStockAgeLog": '''
                INSERT INTO ff_wms.fw_in_stock_age (sku, num, inventory_type, status, create_time, update_time) VALUES ('{}', {}, {}, {}, '{}', '{}')
            ''',
            "getStockAge": '''
                SELECT * FROM ff_wms.fw_in_stock_age WHERE sku = '%s';
            ''',
            "getGoodsSkuBk": '''
                SELECT platform_sku, barcode FROM ff_wms.fw_goods_sku_bk WHERE barcode <> '' GROUP BY platform_sku, barcode;
            ''',
            "getPskuMapping": '''
                SELECT * FROM ff_wms.fw_psku_mapping WHERE sku = '%s';
            ''',
            "getSkuList": '''
                SELECT sku, warehouse_code, platform_sku FROM ff_wms.fw_goods_sku WHERE warehouse_code = '%s' GROUP BY sku ORDER BY sku_id ASC LIMIT %s OFFSET %s
            ''',
            "getWmsInventoryNum": '''
                SELECT SUM(IF(quality = 100, available_qty + exp_shelve_qty + occupied_qty + locking_qty + suspense_qty + in_transit_qty, 0)) AS new_num, SUM(IF(quality = 200, available_qty + exp_shelve_qty + occupied_qty + locking_qty + suspense_qty + in_transit_qty, 0)) AS second_num, warehouse_code, sku, platform_code FROM ff_wms.fw_inventory WHERE sku IN ('%s') and `status` <> 200  GROUP BY sku
            ''',
            "pan_ying_check": '''
                SELECT * FROM ff_wms.fw_inventory_log WHERE sku = '%s' ORDER BY create_time DESC LIMIT 1;
            ''',
            "second_pan_ying_check": '''
                SELECT * FROM ff_wms.fw_inventory_log WHERE sku = '%s' AND business_type = 'ADJUST_ADD' AND quality = 200 ORDER BY create_time DESC LIMIT 1;
            ''',
            "second_inventory_check": '''
                SELECT SUM(available_qty + exp_shelve_qty + occupied_qty + locking_qty + suspense_qty + in_transit_qty) AS num, warehouse_code, sku, platform_code FROM ff_wms.fw_inventory WHERE sku = '%s' AND quality = 200
            ''',
            "getWarehouseCodeRecordNum": '''
                SELECT COUNT(DISTINCT sku) AS num FROM ff_wms.fw_goods_sku WHERE warehouse_code = '%s'
            ''',
            "fix_data_check": '''
                SELECT SUM(to_available_qty) AS num FROM ff_wms.fw_inventory_log WHERE sku = '%s' AND business_type = 'FIXDATA';
            ''',
            "direct_move_check": '''
                SELECT * FROM ff_wms.fw_inventory_log WHERE sku = '%s' AND business_type = 'DIRECT_MOVE' LIMIT 1;
            ''',
            "getWmsGoodsInfo": '''
                SELECT * FROM ff_wms.fw_goods_sku WHERE platform_sku = '%s' AND warehouse_code = '%s';
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
