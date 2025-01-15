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
                select sku from stocks where last_synced_at >= '%s' and last_synced_at <= '%s' and sku in('P008CT8SX','P003JRZ83')  order by id desc limit %s OFFSET %s;
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
                SELECT * FROM pangu.category_attribute WHERE attr_id IN (%s)
            ''',
            "copyPanguWebAttributeData": '''
                SELECT * FROM pangu_website.attribute WHERE `value` IN ('%s') AND `name` = '%s'
            ''',
            "copyPanguWebAttributeLanguageData": '''
                SELECT * FROM pangu_website.attribute_languages_v2 WHERE attr_id IN (%s)
            ''',
            "copyPanguWebCategoryAttributeData": '''
                SELECT * FROM pangu_website.category_attribute WHERE attr_id IN (%s) AND cat_id = %s
            ''',
            "copyPanguStyleData": '''
                SELECT * FROM pangu.style WHERE `value` IN ('%s') AND `name` = '%s'
            ''',
            "copyPanguStyleLanguageData": '''
                SELECT * FROM pangu.style_languages WHERE style_id IN (%s)
            ''',
            "copyPanguCategoryStyleData": '''
                SELECT * FROM pangu.category_style WHERE style_id in (%s)
            ''',
            "copyPanWebStyleData": '''
                SELECT * FROM pangu_website.style WHERE `value` IN ('%s') AND `name` = '%s'
            ''',
            "copyPanWebStyleLanguageData": '''
                SELECT * FROM pangu_website.style_languages WHERE style_id IN (%s)
            ''',
            "copyPanWebCategoryStyleData": '''
                SELECT * FROM pangu_website.
            ''',
            "getWebAttributeDiff": '''
                SELECT
                        tmp.attr_lang_id,
                        tmp.color,
                        tmp.languages_id,
                        tmp.attr_values,
                        tc.languages_id AS tmp_languages_id,
                        tc.`value` AS tmp_value 
                FROM
                        (
                        SELECT
                            a.`name`,
                            a.`value` AS color,
                            alv.attr_id,
                            alv.languages_id,
                            alv.attr_values,
                            alv.attr_lang_id
                        FROM
                            attribute a
                            INNER JOIN attribute_languages_v2 alv ON a.id = alv.attr_id 
                        WHERE
                            a.`value` IN ('%s') 
                            AND a.is_delete = 0 
                            AND alv.languages_id IN ('%s') 
                        ) AS tmp
                        LEFT JOIN tmp_color tc ON tc.color = tmp.color 
                        AND tc.languages_id = tmp.languages_id 
                HAVING
                    attr_values <> tmp_value;
            ''',
            "getWebStyleDiff": '''
                SELECT
                        tmp.sl_id,
                        tmp.color,
                        tmp.languages_id,
                        tmp.`value`,
                        tc.languages_id AS tmp_languages_id,
                        tc.`value` AS tmp_value 
                    FROM
                        (
                        SELECT
                            s.`name`,
                            s.`value` AS color,
                            sl.style_id,
                            sl.languages_id,
                            sl.`value`,
                            sl.sl_id
                        FROM
                            style s
                            INNER JOIN style_languages sl ON s.id = sl.style_id  
                        WHERE
                            s.`value` IN ('%s') 
                            AND s.is_delete = 0 
                            AND sl.languages_id IN ('%s') 
                        ) AS tmp
                        LEFT JOIN tmp_color tc ON tc.color = tmp.color 
                        AND tc.languages_id = tmp.languages_id 
                    HAVING
                        value <> tmp_value;
            ''',
            "getPanAttributeDiff": '''
                SELECT
                        tmp.id,
                        tmp.color,
                        tmp.languages_id,
                        tmp.`value`,
                        tc.languages_id AS tmp_languages_id,
                        tc.`value` AS tmp_value 
                    FROM
                        (
                        SELECT
                            a.`name`,
                            a.`value` AS color,
                            alv.attr_id,
                            alv.languages_id,
                            alv.`value`,
                            alv.id
                        FROM
                            pangu.attribute a
                            INNER JOIN pangu.attribute_languages alv ON a.id = alv.attr_id 
                        WHERE
                            a.`value` IN ('%s') 
                            AND a.is_delete = 0 
                            AND alv.languages_id IN ('%s') 
                        ) AS tmp
                        LEFT JOIN pangu_website.tmp_color tc ON tc.color = tmp.color 
                        AND tc.languages_id = tmp.languages_id 
                    HAVING
                        `value` <> tmp_value;
            ''',
            "getPanStyleDiff": '''
                SELECT
                        tmp.id,
                        tmp.color,
                        tmp.languages_id,
                        tmp.`value`,
                        tc.languages_id AS tmp_languages_id,
                        tc.`value` AS tmp_value 
                    FROM
                        (
                        SELECT
                            s.`name`,
                            s.`value` AS color,
                            sl.style_id,
                            sl.languages_id,
                            sl.`value`,
                            sl.id
                        FROM
                            pangu.style s
                            INNER JOIN pangu.style_languages sl ON s.id = sl.style_id  
                        WHERE
                            s.`value` IN ('%s') 
                            AND s.is_delete = 0 
                            AND sl.languages_id IN ('%s') 
                        ) AS tmp
                        LEFT JOIN pangu_website.tmp_color tc ON tc.color = tmp.color 
                        AND tc.languages_id = tmp.languages_id 
                    HAVING
                        `value` <> tmp_value;
            ''',
            "getPanguStockData": '''
                SELECT sku, available_num, available_tryon_num FROM stocks WHERE sku in ('%s')
            ''',
            "getValidationData": '''
                select * from goods_validation where goods_id in ('%s')
            ''',
            "getGoodsImageColor": '''
                select * from goods_gallery_v2 where goods_id = %s and url = '%s';
            ''',
            "getPanScreenData": '''
                select * from goods_color_img
            ''',
            "getShippingGoodsLog": '''
                select * from category_shipping_fee_log
            ''',
            "getGoodsStyleImg": '''
                select * from goods_color_img;
            ''',
            "getGoodsStatus": '''
                select id from goods where id in ('%s') and is_on_sale = 0
            ''',
            "getCloneId": '''
                select * from goods where source_id = %s
            ''',
            "getSonImgStyle": '''
                select 
                        count(gci.gci_id) as num, g.cat_id 
                from 
                        goods_color_img gci 
                inner join goods g on g.id = gci.goods_id 
                where 
                        gci.goods_id = %s and g.cat_id >= 400
            ''',
            "getStyleImgByCat": '''
                SELECT
	gci.goods_id,
	g.cat_id,
	count( gci.gci_id ) AS num 
FROM
	goods_color_img gci
	INNER JOIN goods g ON g.id = gci.goods_id 
	INNER JOIN goods_style_v2 gsv on gsv.goods_id =  gci.goods_id and gci.style_id = gsv.style_id and gsv.is_delete = 0
WHERE
	g.cat_id IN (%s) 
	AND g.is_on_sale = 1
	AND gci.is_delete = 0 
GROUP BY
	gci.goods_id
            ''',
            "getStockData": '''
                select sku as psku, sku_tag, facility_id, available_num, available_tryon_num, available_sample_num from facility_stocks where facility_id = %s
            ''',
            "getSkuPid": '''
                select sku, product_sn as pid from product_sku where sku in ('%s')
            ''',
            "getClothsData": '''
                SELECT
                    g.id AS gid,
                    g.pid,
                    gss.sku,
                    gss.psku,
                    s1.value as color,
                    s2.value as `size`,
                    c.cat_name as small_cat,
                    pc.name as cat_name
                FROM
                    pangu_website.goods AS g
                    INNER JOIN pangu_website.category c ON c.id = g.cat_id
                    INNER JOIN pangu_website.goods_special_sku gss on gss.goods_id = g.id
                    INNER JOIN pangu.category AS pc ON pc.id = c.pangu_id
                    INNER JOIN pangu_website.style s1 ON s1.id = gss.color_id
                    INNER JOIN pangu_website.style s2 ON s2.id = gss.size_id
                WHERE
                    c.parent_id = %s
                    and g.is_on_sale = 1
                    and g.is_display =1
                    and g.is_delete = 0
            ''',
            "getSkuFacility": '''
                SELECT facility_id, sku FROM facility_stocks WHERE sku IN ('%s')
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
