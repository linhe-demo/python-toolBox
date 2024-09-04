from pkg.Website import Website

if __name__ == "__main__":
    languageList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '12', '16', '24', '29']

    colorList = ['Burgundy', 'Champagne', 'Dark Green', 'Dark Navy', 'Fuchsia', 'Gold', 'Ivory', 'Lavender',
                 'Light Blue', 'Lilac', 'Pearl Pink', 'Regency', 'Royal Blue', 'Silver', 'Sky Blue', 'Watermelon',
                 'Chocolate', 'Grape', 'Mint Green', 'Pool', 'Steel Grey', 'Taupe', 'Blushing Pink', 'Daffodil',
                 'Ink Blue', 'Mist', 'Ocean Blue', 'Jade', 'Candy Pink', 'Dusty Rose', 'Dusty Blue', 'Celadon', 'Blush',
                 'Stormy', 'Navy Blue', 'Cabernet', 'Coral', 'Wisteria', 'Spa', 'Papaya', 'Mulberry', 'Dusk', 'Orchid',
                 'Tahiti', 'Peacock', 'Vermilion', 'Slate Blue', 'Petal', 'Mauve', 'Vintage Mauve', 'Plum',
                 'Hunter Green', 'Sage Green', 'Cinnamon Rose', 'Basil', 'Dusty Lavender', 'Emerald', 'Agave',
                 'Desert Rose', 'Ice Blue', 'Sand', 'French Blue', 'Bronzer', 'Blue', 'Brown', 'Green', 'Grey', 'Black',
                 'Orange', 'Pink', 'Purple', 'Red', 'White', 'Yellow', 'As Picture', 'Florals', 'Neutral', 'Peach Fuzz',
                 'Peony', 'Sea Glass', 'Rosewood', 'Sage Green Dream', 'Pink Lavender'
                 ]
    Website(param=colorList, param2=languageList).colorTranslate()
