from pkg.panGu import PanGu

if __name__ == "__main__":
    categoryList = [7]
    colorList = ["Emerald Blooms", "Navy Petal", "Scarlet Garden","Forest Green Dream"]

    for i in categoryList:
        print("begin category {} ".format(i))

        for m in ["Shop By Color", "Shown Color", "Color"]:
            PanGu(param=i, param2=colorList, parma3=m).moveAttributeData()

        for n in ["ImageColor"]:
            PanGu(param=i, param2=colorList, parma3=n).moveStyleData()

