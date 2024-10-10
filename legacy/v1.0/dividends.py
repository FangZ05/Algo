#calculates the dividend yield of a stock

def dividend(ydata):
    return sum(ydata.dividends[-4:])

def divYield(ydata, lastprice):
    return dividend(ydata)/lastprice