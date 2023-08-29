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
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
