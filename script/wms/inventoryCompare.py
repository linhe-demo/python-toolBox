from pkg.wms import Wms

if __name__ == "__main__":  # wms 与 tms 库存对比工具
    # 'FFWH0007': 'UK Warehouse'
    # 'FFWH0008': 'US Warehouse-Middle'
    # 'FFWH0036': 'DE Warehouse'
    # 'FFWH0039': 'AU Warehouse-JD'
    # 'FFWH0063': 'CA Warehouse'
    warehouseList = {'FFWH0007': 'UK Warehouse'}
    Wms(warehouseId=warehouseList, path="../.././data/InventoryCompared.xlsx").inventoryCompare()