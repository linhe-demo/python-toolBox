from pkg.panGu import PanGu

if __name__ == "__main__":
    facilityList = {
        1049275062: 'UK',
        1049275063: 'US',
        2640152423: 'DE',
        2771772189: 'AU',
        3142292305: 'CA'
    }

    PanGu(param=facilityList, path="../.././data/panguStock.xlsx").inventoryStatistics()
