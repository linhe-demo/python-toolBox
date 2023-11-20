from common.warehouseEnum import WarehouseEnum
from pkg.erp import Erp

if __name__ == "__main__":
    Erp(orderSn='3719780410-c', warehouse=WarehouseEnum.Guangdong.value).transfer()  # 采购单或批量采购单订单转仓sql生成脚本
