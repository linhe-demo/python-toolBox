from common.warehouseEnum import WarehouseEnum
from pkg.erp import Erp

if __name__ == "__main__":
    Erp(orderSn='7021718926-c', warehouse=WarehouseEnum.Suzhou.value).transfer()  # 采购单或批量采购单订单转仓sql生成脚本 orderSn: 采购单号， warehouse：需要转的仓库
