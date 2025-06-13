import json

from pkg.Fdfd import Fdfd

if __name__ == '__main__':
    Fdfd(param="../.././data/supplier/request/refresh_supplier.xlsx", path="../.././data/supplier/response/refresh_supplier.txt", operation_type="order").getSupplierTransferInfo()