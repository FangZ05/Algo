import analysis as an
import numpy as np
import pandas as pd
import pytz
import datetime as dt
import pandas_ta as ta
import fundamentals
import sys
import os
import dataget.yfinData as ydata
import fundamentals.finFundamentals

nytz = pytz.timezone('US/Eastern')
tz = "Australia/Brisbane"
localtz = pytz.timezone(tz)
now = dt.datetime.now(localtz)


def get_stock_data(ticker, timeframe, update = False, chrono = False, period=None):
    """get the local stock data as a dataframe
    
    ticker: ticker of the stock
    timeframe: timeframe that was interested
    period: number of datapoints are requested
    
    Special note: local df are stored with latest data at the top
    """
    
    #define the path to stock
    path = f'data/{ticker}'
    filepath = f"{path}/{ticker}_{timeframe}.csv"
    
    #check if update is needed
    if update:
        ydata.getTickerData(ticker, timeframe)
        
    #get the dataframe
    pricedf = pd.read_csv(filepath, nrows = period)

    #ask if we want the stock to be arranged in chronological order
    if chrono:
        pricedf = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so oldest is at top
    
    return pricedf



def rng_date(pricedf, period=30):
    """
    generate a random date from the pricedf
    
    pricedf: price data of the stock
    period: must have minimum this number of period after the generated date
    """
    #get the time dataframe
    time = pricedf['Time']
    
    #specify the allowed range of the sample
    end = now - dt.timedelta(days = period) #to avoid out of range error
    allowedSample = time[time < end]
    
    #collect 1 sample
    sample = allowedSample.sample()
    
    return sample.iloc[0]

def buy(principle, price, shares=None):
    """
    Calculates the necessary parameters when you buy a stock
    """
    if (shares==None) or ((price*shares)>principle):
        shares = principle//price
    cashflow = -1 * shares * price
    principle = principle + cashflow
    return principle, cashflow, shares
    
def sell(principle, price, shares):
    """
    Calculates the necessary parameters when you sell a stock
    """
    cashflow = price*shares
    principle = principle + cashflow
    return principle, cashflow, shares

def benchmark(pricedfChrono, principle, start, period=30):
    """"
    a backtest benchmark using buy and hold strategy. Used to calculate alpha.
    
    pricedfChrono: price data of the stock in chronological order (oldest at top)
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    
    """
    end = start + dt.timedelta(days=period)
    

    priceChrono = pricedfChrono['Close'] #get the closing price for non-candlestick purpose
    timeChrono = pricedfChrono['Time']
    
    for i in timeChrono:
        if i > start:
            start = i
            break

    givendf = pricedfChrono[((pricedfChrono['Time'] > start ) & (pricedfChrono['Time'] < end))]
    givenTime = pd.to_datetime(givendf['Time'], utc=True).dt.tz_convert(nytz).dt.tz_localize(None)
    timeChrono = pd.to_datetime(timeChrono, utc=True).dt.tz_convert(nytz).dt.tz_localize(None)
    
    sharepriceInit = givendf.iloc[0]['Close']
    sharepriceEnd = givendf.iloc[-1]['Close']
    portfolioStock = 0
    #buy the stock
    if principle > sharepriceInit:
        principle, cashflow, shares = buy(principle, sharepriceInit, principle)
        portfolioStock = portfolioStock + shares
        
    #sell the stock
    if portfolioStock > 0:
        principle, cashflow, shares = sell(sharepriceEnd, portfolioStock)
    return principle
    
def backtest(pricedfChrono, principle, criteria, start, period=30, verbose = False):
    """
    a backtest strategy for 26 period trend, with 1 period delayed momentum
    
    pricedfChrono: price data of the stock in chronological order (oldest at top)
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    """
    end = start + dt.timedelta(days=period)
    

    priceChrono = pricedfChrono['Close'] #get the closing price for non-candlestick purpose
    timeChrono = pricedfChrono['Time']
    
    for i in timeChrono:
        if i > start:
            start = i
            break

    givendf = pricedfChrono[((pricedfChrono['Time'] > start ) & (pricedfChrono['Time'] < end))]
    givenTime = pd.to_datetime(givendf['Time'], utc=True).dt.tz_convert(nytz).dt.tz_localize(None)
    timeChrono = pd.to_datetime(timeChrono, utc=True).dt.tz_convert(nytz).dt.tz_localize(None)

    bars = 5
    period = 26
    portfolioStock = 0
    buytrade = 0
    selltrade = 0

    for i in givenTime:
        loc = pricedfChrono[timeChrono==i].index[0]
        iloc = pricedfChrono.index.get_loc(loc)
        row = pricedfChrono.iloc[iloc]
        shareprice = row['Close']
        trend = []
        for j in range(1, 1+bars):
            if iloc - j < period:    
                ilocstart = 0
            else:
                ilocstart = iloc - period - j
            trendline = an.trendbasic(priceChrono[ilocstart:iloc-j], period)
            trend.append(trendline)

        trend = np.array(trend)[::-1]
        accel = np.gradient(trend)

        roc = trend[-1]
        momentum = accel[-2]


        if ((roc > 0) & (momentum > 0)):
            if principle > shareprice:
                principle, cashflow, shares = buy(principle, shareprice, principle)
                portfolioStock = portfolioStock + shares
                if shares > 0:
                    buytrade += 1
                if verbose: 
                    print(f"Current iteration: {i}")
                    print(f"Current trend: {trend}")
                    print(f"Current time: {row['Time']}")
                    print(f"Current roc: {roc}")
                    print(f"Current lag momentum: {momentum}")
                    print(f"buying stock at price = {shareprice}")
                    print(f"Current principle = {principle}")
                    print(f"number of buy trades = {buytrade}")
        if momentum < 0:
            if portfolioStock > 0:
                principle, cashflow, shares = sell(shareprice, portfolioStock)
                if portfolioStock > 0:
                    selltrade += 1
                portfolioStock = 0
                if verbose: 
                    print(f"Current iteration: {i}")
                    print(f"Current trend: {trend}")
                    print(f"Current time: {row['Time']}")
                    print(f"Current roc: {roc}")
                    print(f"Current lag momentum: {momentum}")
                    print(f"selling stock at price = {shareprice}")
                    print(f"Current principle = {principle}")
                    print(f"number of sell trades = {selltrade}")
    
    #close all positions
    if portfolioStock > 0:
        principle, cashflow, shares = sell(shareprice, portfolioStock)
        if portfolioStock > 0:
            selltrade += 1
        portfolioStock = 0
    if verbose: 
        print(f"Current iteration: {i}")
        print(f"Current trend: {trend}")
        print(f"Current time: {row['Time']}")
        print(f"Current roc: {roc}")
        print(f"Current lag momentum: {momentum}")
        print(f"selling stock at price = {shareprice}")
        print(f"Current principle = {principle}")
        print(f"number of sell trades = {selltrade}")
    return principle

def strategyTest(pricedfChrono, principle, period=30, verbose = False):
    
    testresults = []
    testresultsalpha = []
    for i in range(100):
        start = rng_date(pricedfChrono, period)
        buynhold = benchmark(pricedfChrono, principle, start, period)
        strategy = backtest(pricedfChrono, principle, start, period)
        excessreturn = strategy - buynhold
        alpha = excessreturn/principle
        if verbose:
            print(f"test {i}: buy and hold result = {buynhold}")
            print(f"test {i}: strategy result = {strategy}")
            print(f"test {i}: excess return = {excessreturn}")
            print(f"test {i}: alpha = {alpha}")
        testresultsalpha.append(alpha)
        testresults.append(excessreturn)
        
    testresults = np.array(testresults)
    mean = np.mean(testresults)
    median = np.median(testresults)
    
    testresultsalpha = np.array(testresultsalpha)
    meanA = np.mean(testresultsalpha)
    medianA = np.median(testresultsalpha)
    print(f"mean return = {mean}")
    print(f"median return = {median}")
    print(f"mean alpha = {meanA}")
    print(f"median alpha = {medianA}")
    return median
        

        
ticker = "SPY"
timeframe = "1d"
update=True
pricedf = get_stock_data(ticker, timeframe, update=update)

pricedfChrono = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so oldest is at top

pricedf = pricedf.reset_index(drop=True)
pricedfChrono = pricedfChrono.reset_index(drop=True)

