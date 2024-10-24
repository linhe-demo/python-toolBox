from pkg.panGu import PanGu

if __name__ == "__main__":
    goodsId = [310054, 310050, 309847, 309846, 309845, 309844, 309843, 309841, 301782, 301781, 301777, 301772, 298073,
               298054, 298050, 290698, 290682, 288307, 288283, 255877]
    newGoodsId = []
    for i in goodsId:
        newGoodsId.append(str(i))
    PanGu(param=newGoodsId).getImageColor()
