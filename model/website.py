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
            ''',
            "getWebScreenData": '''
                select * from goods_color_img
            ''',
            "getGoodsPlusData": '''
                select * from goods_extension where  ext_name in ('%s') and goods_id = 150447;
            ''',
            "getGoodsShopByColorImg": '''
                select * from goods_gallery where goods_id = %s and img_url in ('%s') and is_delete = 1
            ''',
            "getGoodsPhotoImg": '''
                select * from goods_gallery where img_id = %s  and is_delete = 1
            ''',
            "getGoodsStyleImg": '''
                        select * from goods_color_img;
            ''',
            "getCategoryAttribute": '''
                select 
				    av.url_attr_name
                from 
			        attribute_v2 av 
                inner join attribute_category_display_filter ac on ac.attr_id = av.attr_id
                where av.attr_name = '%s'
                and ac.cat_id = %s and av.parent_id <> 0 and av.is_delete = 0;
            ''',
            "getCombineProductSql": '''
                	select goods_id, ext_value from goods_extension where ext_name = 'combination_product_id';
            ''',
            "getCombineGoods": '''
                select * from combination_products where id = %s
            ''',
            "getCombineTpl": '''
                select * from combination_product_tpls where id = %s
            ''',
            "getBuyTheLookData": '''
                select ge.*, g.cat_id from goods_extension ge inner join goods g on ge.goods_id = g.goods_id where ge.ext_name = 'buy_the_look_data';
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
