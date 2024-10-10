import pandas as pd
import numpy as np

def vixhist(pricedf, period=30):
    """
    Calculates the historical volatility of the given stock.

    pricedf: dataframe of the stock data
    period: number of period to calculate volatility from
    """
    #fail safe if length of array is shorter than period
    if pricedf.shape[0] < period:
        period = pricedf.shape[0]

    #get the closing price of stock for a given period
    price = pricedf['Close'].iloc[0:period]

    #calculate the standard deviation as a percentage
    stdv = price.std()/price.iloc[0]

    return stdv

def varhist(pricedf, period=30):
    """
    Calculates the historical variance of the given stock.

    pricedf: dataframe of the stock data
    period: number of period to calculate volatility from
    """
    #fail safe if length of array is shorter than period
    if pricedf.shape[0] < period:
        period = pricedf.shape[0]

    #get the closing price of stock for a given period
    price = pricedf['Close'].iloc[0:period]

    #calculate the standard deviation as a percentage
    stdv = price.std()

    return stdv

def vvixhist(pricedf, vperiod=30, period=30):
    """
    Calculates the volatility of historical volatility (v-vol) of the given stock.

    pricedf: dataframe of the stock data
    vperiod: number of period to calculate volatility from
    period: number of period to calculate v-vol from
    """

    #fail safe if length of array is shorter than period
    if pricedf.shape[0] < period:
        period = pricedf.shape[0]

    #define the list of volatilities
    vvix = []

    #calculate volatility for the past {period} days
    for i in range(period):
        price = pricedf.drop(pricedf.head(i).index) #start from day i
        stdv = vixhist(price, vperiod) #calculate volatility
        vvix.append(stdv) #add to list

    #find standard deviation of volatility
    stdvv = pd.DataFrame(vvix).std()[0]

    return stdvv

def vvarhist(pricedf, vperiod=30, period=30):
    """
    Calculates the volatility of historical variance (v-var) of the given stock.

    pricedf: dataframe of the stock data
    vperiod: number of period to calculate volatility from
    period: number of period to calculate v-var from
    """

    #fail safe if length of array is shorter than period
    if pricedf.shape[0] < period:
        period = pricedf.shape[0]

    #define the list of volatilities
    vvar = []

    #calculate volatility for the past {period} days
    for i in range(period):
        price = pricedf.drop(pricedf.head(i).index) #start from day i
        stdv = varhist(price, vperiod) #calculate volatility
        vvar.append(stdv) #add to list

    #find standard deviation of volatility
    stdvv = pd.DataFrame(vvar).std()[0]

    return stdvv

def trendbasic(array, period):
    """
    generate a simple linear trend of a given array over the given period

    array: the given array. Note this must be either pandas dataframe, its derivative, or numpy array
    period: number of datapoint
    """
    #fail safe if array is way too short
    if array.shape[0] < 2:
        return 0
    
    #fail safe if length of array is shorter than period
    if array.shape[0] < period:
        period = array.shape[0]

    #generate x & y values
    x = np.arange(0, period, 1)
    y = array[0:period]

    #generate a linear fit
    fit = np.polyfit(x, y, 1)

    #get the gradient of the fit
    trend = fit[0]

    return trend