from pkg.db import Db
from pkg.panGu import PanGu

if __name__ == "__main__":
    PanGu(param="shopbycolor", path="../.././data/shop_by_color.xlsx").getColorImgDefaultData()

    # goodsId = []
    # PanGu(param="shopbycolor", param2= goodsId, path="../.././data/shop_by_color_website.xlsx").getHistoryData()

    # categoryIds = ["C423"]
    # PanGu(param=categoryIds, path="../.././data/cover_data.xlsx").fixHistoryColorImageData()




