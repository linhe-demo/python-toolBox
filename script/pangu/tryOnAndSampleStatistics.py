from pkg.panGu import PanGu

if __name__ == "__main__":

    typeList = {
        400: '试衣',
        420: '样衣'
    }

    PanGu(param=typeList, path="../.././data/tryOnAndSample.xlsx").tryOnAndSampleStatistics()
