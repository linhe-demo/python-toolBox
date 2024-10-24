from pkg.panGu import PanGu

if __name__ == "__main__":
    header = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 29]
    PanGu(param="../.././data/colorTranslate.xlsx", param2=header).getColorData()