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
                           av.attr_values AS color,
                           alv.languages_id,
                           alv.attr_values  as `value`
                FROM       attribute_v2 av  
                INNER JOIN attribute_languages_v2 alv ON av.attr_id = alv.attr_id AND av.attr_name = alv.attr_name 
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
                INNER JOIN  style_languages sl ON s.style_id = sl.style_id AND s.`name` = sl.`name` 
                WHERE
                        s.`value` IN ('%s') 
                AND 
                        sl.languages_id IN ('%s');
            '''
        }

    def getSql(self):
        return self.sqlMap().get(self.index)
