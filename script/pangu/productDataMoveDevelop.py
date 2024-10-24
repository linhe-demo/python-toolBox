from pkg.panGu import PanGu

if __name__ == "__main__":
    categoryList = [7]
    colorList = ['Coral Sunset', 'Sage Serenity', 'Aqua Blooms', 'Mint Green Blooms', 'Petal Pink Dream']

    for i in categoryList:
        print("begin category {} ".format(i))

        for m in ['Shop By Color', 'Shown Color', 'Color']:
            PanGu(param=i, param2=colorList, parma3=m).moveAttributeData()

        for n in ["Color", "ImageColor"]:
            PanGu(param=i, param2=colorList, parma3=n).moveStyleData()
