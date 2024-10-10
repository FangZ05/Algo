import yfinData as ydata
import numpy as np
import pandas as pd
import analysis as an
import matplotlib.pyplot as plt
import datetime as dt
import pytz

nytz = pytz.timezone('US/Eastern')
    
def get_stock_data(ticker, timeframe, period=None):
    #get the stock data as a dataframe
    path = f'data/{ticker}'
    filepath = f"{path}/{ticker}_{timeframe}.csv"
    
    #get or update data using yfinance
    
    #get the dataframe
    pricedf = pd.read_csv(filepath, nrows = period)
    
    return pricedf

update = True
ticker = "IWM"
timeframe = "1h"

if update:
    ydata.getTickerData(ticker, timeframe)

pricedf = get_stock_data(ticker, timeframe)
price = pricedf['Close'] #get the closing price for non-candlestick purpose

pricedf['Time'] = pd.to_datetime(pricedf['Time'], utc=True).dt.tz_convert(nytz).dt.tz_convert(None)

pricedfChrono = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so oldest is at top
priceChrono = pricedfChrono['Close'] #get the closing price for non-candlestick purpose

bars = 1000 #look back #of bars
period = 26 #period for trend
trend=[]
for i in range(1, 1+bars):
    trendline = an.trendbasic(priceChrono[-period-i:-i], period)
    trend.append(trendline)

trend = np.array(trend)[::-1]
accel = np.gradient(trend)

x = np.arange(-trend.shape[0], 0, 1)
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.plot(x, trend)