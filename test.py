import pandas as pd
import time
import datetime as dt
import pytz
import os
import options.optionsBlackScholes

start_time = time.time()
def vixhist(pricedf, period=30):
    """
    Calculates the historical volatility of the given stock.

    pricedf: dataframe of the stock data
    period: number of period to calculate volatility from
    """
    #get the closing price of stock for a given period
    price = pricedf['Close'].iloc[0:period]

    #calculate the standard deviation as a percentage
    stdv = price.std()/price.iloc[0]

    return stdv


def vvixhist(pricedf, vperiod=30, period=30):
    """
    Calculates the volatility of historical volatility (v-vol) of the given stock.

    pricedf: dataframe of the stock data
    vperiod: number of period to calculate volatility from
    period: number of period to calculate v-vol from
    """
    #define the list of volatilities
    vvix = []

    #calculate volatility for the past {period} days
    for i in range(period):
        price = pricedf.drop(pricedf.head(i).index) #start from day i
        stdv = vixhist(price, vperiod) #calculate volatility
        vvix.append(stdv) #add to list

    #find standard deviation of volatility
    stdvv = pd.DataFrame(vvix).std()
    
    return stdvv
print("--- %s seconds ---" % (time.time() - start_time))
