from pkg.wms import Wms

if __name__ == "__main__":
    pskuList = ['QFZ-ND13510', 'ZBHJYLF39118', 'YJLF41572', 'MOLF32162', 'FLFZ-ND36012', 'ECXS71070', 'ECXS71110',
                'ECXS14831', 'JXXLFS22927', 'ECXS4293', 'XHLF30330', '09D1QV2', 'BHBYFZ30157', 'ZBHBXDH10126']
    Wms(warehouseId=36, psku=pskuList).createLog()
