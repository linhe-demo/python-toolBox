import json

import pandas as pd
from pandas import Timestamp
from pkg.panGu import PanGu
from tools.file import File

if __name__ == "__main__":
    # PanGu().getShippingGoodsLog()

    # 读取 Excel 文件
    excel_file_path = '../.././data/test.xlsx'
    sheet_name = 'Sheet1'  # 你可以根据需要更改工作表名称
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    # 将 DataFrame 转换为字典列表（每行一个字典）
    data = df.to_dict(orient='records')


    class TimestampEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Timestamp):
                return obj.isoformat()
                # 你可以在这里添加对其他类型的处理
            return json.JSONEncoder.default(self, obj)

            # 示例数据


    # 使用自定义编码器序列化
    json_data = json.dumps(data, cls=TimestampEncoder)

    # 打印或保存 JSON 字符串
    File(path="../.././data/json.txt", txtData=json_data).writeTxtInline()

