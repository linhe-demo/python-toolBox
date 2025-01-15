from pkg.erp import Erp

if __name__ == "__main__":
    Erp(param="c%", filePath="../.././data/skuStatus.xlsx").getSkuStatus()
