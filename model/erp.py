# erp据库操作类

class ErpDatatable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "ecs_goods_count": '''
                SELECT COUNT(*) as total FROM %s WHERE external_cat_id = %s
            ''',
            "ecs_goods_ec_goods_by_cat_id_prod": '''
                SELECT * FROM %s WHERE external_cat_id = %s ORDER BY goods_id ASC LIMIT %s, %s
            ''',
            "ecs_goods_ec_goods_save_test": '''
                INSERT INTO %s VALUES (%s)
            ''',
            "check_sku_exist": '''
                SELECT * FROM ecs_goods WHERE uniq_sku = '%s'
            ''',
            "get_order_info": '''
                SELECT * FROM ecshop.ecs_order_info WHERE order_sn = '%s'
            ''',
            "update_order_info": '''UPDATE ecshop.ecs_order_info SET facility_id = '%s' WHERE order_id = '%s'; ''',
            "get_purchase_info": '''
                SELECT * FROM ecshop.batch_goods_purchase_request WHERE order_id IN ('%s')
            ''',
            "update_purchase_info": '''UPDATE ecshop.batch_goods_purchase_request SET facility_id = '%s' WHERE order_id = '%s'; ''',
            "get_delivery_info": '''
                SELECT * FROM eris.delivery_list_detail WHERE order_id IN ('%s')
            ''',
            "update_delivery_info": '''UPDATE eris.delivery_list_detail SET facility_id = '%s' WHERE order_id = '%s';''',
            "get_order_info_money": '''
                SELECT
	sum( order_amount ) AS t,
	LEFT ( order_time, 7 ) AS s 
FROM
	ecs_order_info 
WHERE
	order_time >= '%s 00:00:00' 
	AND order_time <= '%s 23:59:59' 
	AND order_status <> 2 
GROUP BY
	s;
            ''',
            "getSku": '''
                SELECT
	egm.uniq_sku
FROM
	ecshop.ecs_goods_mapping egm 
WHERE
	1 
	AND egm.uniq_sku LIKE '%s'
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
