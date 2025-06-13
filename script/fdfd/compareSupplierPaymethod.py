import json

from pkg.Fdfd import Fdfd

if __name__ == '__main__':

    Fdfd(param="../.././data/supplier/request/supplier_system.xlsx", path="../.././data/supplier/request/supplier_back.xlsx").compareSupplier()

