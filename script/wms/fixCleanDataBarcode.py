from pkg.wms import Wms

if __name__ == "__main__":  # 数据清洗 将历史数据中的barcode 写入pskuMapping中
    Wms().fixBarcode()
