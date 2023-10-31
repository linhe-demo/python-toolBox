from pkg.erp import Erp

if __name__ == "__main__":
    Erp(filePath="../.././data/skuc207g.txt").checkSkuExists()  # 查询外部文件中的sku，在erp中不存在的有哪些
