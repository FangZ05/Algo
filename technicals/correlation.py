"""
All functions used to calculate the correlation between two stocks

Used as a way to convert greeks of one stock's option to another

"""


def corr(stock1, stock2, price='Close', method = 'pearson'):
    """
    Calculates the correlation between two given stocks.

    Inputs:
        stock1: dataframe of stock 1
        stock2: dataframe of stock 2
        price: which one of OHLC is used
        method: correlation method used to calculate the correlation. 
            Default Pearson.
    """

    #grab the price
    series1 = stock1[price]
    sereis2 = stock2[price]

    #calculate correlation
    correlation = series1.corr(sereis2, method = method)

    return correlation

if __name__== '__main__':
    import dataget.dataget as data
    