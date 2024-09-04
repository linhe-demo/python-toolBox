from pkg.panGu import PanGu

if __name__ == "__main__":
    categoryList = [402, 422]
    colorList = ['Sage Green Dream', 'Pink Lavender']

    for i in categoryList:
        print("begin category {} ".format(i))
        # PanGu(param=i, param2=colorList, parma3="Sale Color").moveAttributeData()

        PanGu(param=i, param2=colorList, parma3="Color").moveStyleData()
