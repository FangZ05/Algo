#%matplotlib auto
"""
Main script of the trading alogrithm
All time in GMT
"""
#os manipulation libraries
from pathlib import Path
import os
import csv
import datetime as dt
import time
import pytz

start_time = time.time()

#library of functions for trading
import indicators as ind
import dataget.yfinData as ydata
import charting.charting_old as charts
import optionsBlackScholes as options
import optionsStrats as strats
import dividends as div
import fixed_income as fixed
import misc
import analysis as an
import utilities.data_cleaning as clean
import fundamentals.finFundamentals as finf
import strategies.technicalStrats as strat
import strategies.dailyohlc as ohlcstrat
import backtest as bt
#market analysis libraries
import yfinance as yf
import pandas_ta as ta
import technicals.dailyohlc as daily

#scientific libraries
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf
import math

#import ploting libraries
import plotly as plty
import plotly.graph_objects as go



#Other useful libraries
import webbrowser #web browser interaction
#from tempfile import NamedTemporaryFile

#charting tutorial libraries
import requests
from lightweight_charts import Chart
import asyncio
import nest_asyncio

ohlc = ['Open','High','Low','Close']

def stock_data_get(ticker, timeframe, update = False, chrono = False, period=None):
    """get the local stock data as a dataframe
    
    ticker: ticker of the stock
    timeframe: timeframe that was interested
    period: number of datapoints are requested
    
    Special note: local df are stored with latest data at the top
    """
    
    #define the path to stock
    path = f'data/{ticker}'
    targetfile = f"{path}/{ticker}_{timeframe}.csv"
    
    #check if update is needed
    if update:
        ydata.getTickerData(ticker, timeframe)
        
    #get the dataframe
    pricedf = pd.read_csv(targetfile, nrows = period)

    #ask if we want the stock to be arranged in chronological order
    if chrono:
        pricedf = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so oldest is at top
    
    #standardize the data using cleaning module
    pricedf = clean.stock_data_process(pricedf)
    
    return pricedf
'''
#global variables
tz = "Australia/Brisbane"
localtz = pytz.timezone(tz)

now = dt.datetime.now(localtz)
#get ticker
#ticker = input("Enter Stock symbol")
#timeframe = input("Enter timeframe")
ticker = "IWM"
timeframe = '1h'



ticker = ticker.upper() #converts ticker to uppercase letters

#=================Run Program=======================#


#get the stock data

#get stock info
tdata = yf.Ticker(ticker)
info = ydata.getInfoLocal(ticker)
'''
def showchart():
    chart = Chart()
    chart.set(pricedf)
    chart.show(block=False)


if __name__ == '__main__':
    nest_asyncio.apply()
    nytz = pytz.timezone('US/Eastern')
    ticker = "IWM"
    timeframe = '15m'
    ticker = ticker.upper() #converts ticker to uppercase letters
    update = True
    pricedf = stock_data_get(ticker, timeframe, update=update)
    qqqd = stock_data_get('QQQ', '1d', update=update)
    iwmd = stock_data_get('IWM', '1d', update=update)
    spyd = stock_data_get('SPY', '1d', update=update)
    
    qqq1h = stock_data_get('QQQ', '1h', update=update)
    iwm1h = stock_data_get('IWM', '1h', update=update)
    spy1h = stock_data_get('SPY', '1h', update=update)
    #qqqd['Close'] = qqqd['Adj Close']
    #iwmd['Close'] = iwmd['Adj Close']
    #spyd['Close'] = spyd['Adj Close']
    iwm1m = stock_data_get('IWM', '1m', update=update)
    qqq1m = stock_data_get('QQQ', '1m', update=update)
    spy1m = stock_data_get('SPY', '1m', update=update)
    iwm5m = stock_data_get('IWM', '5m', update=update)
    qqq5m = stock_data_get('QQQ', '5m', update=update)
    spy5m = stock_data_get('SPY', '5m', update=update)
    iwm15m = stock_data_get('IWM', '15m', update=update)
    qqq15m = stock_data_get('QQQ', '15m', update=update)
    spy15m = stock_data_get('SPY', '15m', update=update)
    
    spy = clean.stock_data_reversetime(spy15m)
    qqq = clean.stock_data_reversetime(qqq15m)
    iwm = clean.stock_data_reversetime(iwm15m)
    price = pricedf['Close'] #get the closing price for non-candlestick purpose
    pricedfChrono = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so latest is at top
    priceChrono = pricedfChrono['Close'] #get the closing price for non-candlestick purpose
    #pricedf['Time'] = pd.to_datetime(pricedf['Time'], utc=True).dt.tz_convert(nytz).dt.tz_convert(None)
    #pricedf = pricedf.drop(columns=['Adj Close'])
    #pricedf = pricedf.rename(columns={'Time':'time', 'Open': 'open', 'Close':'close','High':'high','Low':'low','Volume':'volume'}) #rename the date column
    
    testresults = []
    stocks = [spy15m, qqq15m, iwm15m]
    """
    for i in stocks:
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.gap_close_buyAtOpen, benchmark=bt.riskfree, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.gap_close_buyAtOpen, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.minute_range_15, benchmark=bt.riskfree, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.minute_range_15, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.minute_range_15_modified, benchmark=bt.riskfree, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.minute_range_15_modified, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.minute_range_15_modified_sma, benchmark=bt.riskfree, period=5, repeats = 1000, verbose = True))
        testresults.append(bt.strategyTest(i, 10000, strategy=ohlcstrat.minute_range_15_modified_sma, period=5, repeats = 1000, verbose = True))
    for i in testresults:
        print(f'mean excess :{i.mean}')
        print(f'median excess :{i.median}')
        print(f'success rate :{i.success}')
        """
print("--- %s seconds ---" % (time.time() - start_time))
