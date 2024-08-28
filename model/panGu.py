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
            ''',
            "getStockSku": '''
                select sku from stocks where last_synced_at >= '%s' and last_synced_at <= '%s' order by id desc limit %s OFFSET %s;
            ''',
            "getGoodsColorGoodsId": '''
                SELECT 
                            distinct g.id 
                FROM
	                        goods as g
	            INNER JOIN  
	                        goods_gallery_v2 ga ON ga.goods_id = g.id
	            INNER JOIN  
	                        category AS c ON g.cat_id = c.id
                WHERE
	                        g.is_on_sale = 1 
	            AND 
	                        g.is_delete = 0 
	            AND 
	                        g.is_display = 1
	            AND 
	                        g.cat_id = 423
	            AND
	                        c.is_show = 1
	            AND 
	                        ga.type = '%s';
            ''',
            "getGoodsColorInfo": '''
                SELECT 
                            id as image_id, goods_id, type, is_default, concat("https://cdn-4.jjshouse.com/upimg/l/", url) as url, color, cat_id
                FROM
	                        goods_gallery_v2
                WHERE
	                        goods_id IN (%s) 
	            AND 
	                        type = '%s'
	            AND
	                        is_delete = 0
	            AND 
	                        url != ''
                AND 
                            from_project = 'jjshouse';
            ''',
            "getGoodsImageInfo": '''
                SELECT * FROM goods_gallery_v2 WHERE goods_id = %s AND url = '%s'
            ''',
            "tryOnAndSamples": '''
                SELECT * FROM category WHERE parent_id IN (%s)
            ''',
            "getAttrByValue": '''
                SELECT * FROM attribute WHERE `value` IN ('%s')
            ''',
            "getCategoryAttributeMaxSort": '''
                SELECT MAX(display_order) AS `order` FROM category_attribute WHERE cat_id = %s;
            ''',
            "copyPanguAttributeData": '''
                SELECT * FROM pangu.attribute WHERE `value` IN ('%s') AND `name` = '%s'
            ''',
            "copyPanguAttributeLanguageData": '''
                SELECT * FROM pangu.attribute_languages WHERE attr_id IN (%s)
            ''',
            "copyPanguCategoryAttributeData": '''
                SELECT * FROM pangu_website.category_attribute WHERE attr_id IN (%s)
            ''',
            "copyPanguWebAttributeData": '''
                SELECT * FROM pangu_website.attribute WHERE `value` IN ('%s') AND `name` = '%s'
            ''',
            "copyPanguWebAttributeLanguageData": '''
                SELECT * FROM pangu_website.attribute_languages_v2 WHERE attr_id IN (%s)
            ''',
            "copyPanguWebCategoryAttributeData": '''
                SELECT * FROM pangu_website.category_attribute WHERE attr_id IN (%s) AND cat_id = %s
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
