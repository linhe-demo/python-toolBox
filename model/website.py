class websiteTable:
    def __init__(self, index=None):
        self.index = index

    @staticmethod
    def sqlMap():
        return {
            "getTmpColor": '''
                SELECT * FROM pangu_website.tmp_color;
            ''',
            "getAttributeDiff": '''
                SELECT
                           alv.attr_lang_id,
                           av.attr_id,
                           av.url_attr_name,
                           av.attr_values AS color,
                           alv.languages_id,
                           alv.attr_values  as `value`
                FROM       attribute_v2 av  
                INNER JOIN attribute_languages_v2 alv ON av.attr_id = alv.attr_id 
                WHERE
                        av.is_delete = 0 
                        AND av.attr_values IN ('%s') 
                        AND alv.languages_id IN ('%s')
            ''',
            "getStyleDiff": '''
                SELECT
                            sl.sl_id,
                            s.style_id,
                            s.`value` as color,
                            sl.languages_id,
                            sl.`value`
                FROM        style s
                INNER JOIN  style_languages sl ON s.style_id = sl.style_id 
                WHERE
                        s.`value` IN ('%s') 
                AND 
                        sl.languages_id IN ('%s');
            ''',
            "getGoodsIdByCategoryId": '''
                SELECT 
                       *
                FROM
                       style
                WHERE
                       cat_id = %s
                AND 
                      `name` in ('size', 'color') and parent_id <> 0
                        
            ''',
            "getSizeAndColorById": '''
                SELECT * FROM goods_style_black_white WHERE goods_id in (%s) AND black_white = 'white' AND style_name IN ('color', 'size')
            ''',
            "getWebStockData": '''
                SELECT
	                gss.stock,
	                ssm.source_sku as psku
                FROM
                    goods_special_sku gss
                    INNER JOIN sku_sync_map ssm ON gss.sku = ssm.sku 
                WHERE
                    gss.last_update_time > '%s' 
                GROUP BY
                    ssm.source_sku;
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
