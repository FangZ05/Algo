#Misc functions that may or may not be useful

def daily_var(pricedf):
    '''
    calculates the daily variance of a stock

    pricedf: Pandas dataframe of a stock
    '''
    var = pricedf.High-pricedf.Low #daily variance
    pdf = (pricedf.High + pricedf.Low)/2 #price on the day
    pcnt = 100*var/pdf #variance as a percentage
    return  pcnt