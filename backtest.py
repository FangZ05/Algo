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
import fundamentals.finFundamentals as finf
import yfinance as yf
import utilities.data_cleaning as clean
import time
start_time = time.time()
#=====global variables=====#
nytz = pytz.timezone('US/Eastern')
tz = "Australia/Brisbane"
localtz = pytz.timezone(tz)
now = dt.datetime.now(localtz)

class test_results:
    #class for test results so one can store multiple types of them easily
    def __init__(self, mean, median, meanAlpha, medianAlpha, successrate):
        self.mean = mean #mean return in dollar
        self.median = median #median return in dollar
        self.meanAlpha = meanAlpha #mean alpha
        self.medianAlpha = medianAlpha #median alpha
        self.successrate = successrate
        #NOTE: alpha is return compare to market benchmark

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

def portfolio(port, ticker, shares):
    """
    
    """
    port[ticker] = shares
    return port

    
def backtest(pricedfChrono, principle, start, period=30, verbose = False):
    """
    a backtest strategy for 26 period trend, with 1 period delayed momentum
    
    pricedfC: price data of the stock
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
    buyprice = 0
    buytrade = 0
    selltrade = 0
    successtrade = 0
    freeze = False
    principleprev = principle
    def long():
        nonlocal principle
        nonlocal portfolioStock
        nonlocal buytrade
        nonlocal buyprice
        if principle > shareprice:

            principle, cashflow, shares = buy(principle, shareprice)
            portfolioStock = portfolioStock + shares
            if shares > 0:
                buytrade += 1
                buyprice = shareprice
            if verbose: 
                print(f"Current iteration: {i}")
                print(f"Current trend: {trend}")
                print(f"Current time: {row['Time']}")
                print(f"Current roc: {roc}")
                print(f"Current lag momentum: {momentum}")
                print(f"buying stock at price = {shareprice}")
                print(f"Current principle = {principle}")
                print(f"number of buy trades = {buytrade}")
    def short():
        nonlocal principle
        nonlocal portfolioStock
        nonlocal selltrade
        nonlocal principleprev
        nonlocal successtrade
        if portfolioStock > 0:
            principle, cashflow, shares = sell(principle, shareprice, portfolioStock)
            if portfolioStock > 0:
                if principle > principleprev:
                    successtrade += 1
                principleprev = principle
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
        
        if portfolioStock > 0:
            if shareprice < (buyprice * 0.99):
                #stoploss
                short()
                freeze = False
            if shareprice > (buyprice * 1.02):
                #take profit
                short()
                freeze = False

        if ((roc > 0) & (momentum > 0)):
            if not freeze:
                if portfolioStock ==0:
                    long()
                    freeze = True
        #if momentum < 0:
            #short()
            #freeze = False

    
    #close all positions
    short()
    successrate = successtrade/selltrade
    print(f"test: r={successtrade}, s={selltrade}")
    return principle, successrate

def buynhold(pricedfChrono, principle, start, period=30):
    """"
    Buy and hold strategy. 
    Generally used to calculate alpha.
    
    pricedfChrono: price dataframe of the stock in chronological order (oldest at top)
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    
    """

    #calculate the end date
    end = start + dt.timedelta(days=period)
    
    #turn time into its own series
    timeChrono = pricedfChrono['Time']
    
    #make starting time one of the time with in the dataframe
    for i in timeChrono:
        if i > start:
            start = i
            break
    
    #limit the range of data to be only in the given start and end date
    givendf = pricedfChrono[((pricedfChrono['Time'] > start ) & (pricedfChrono['Time'] < end))]
    
    #get the share price at the start and end of the period
    sharepriceInit = givendf.iloc[0]['Close']
    sharepriceEnd = givendf.iloc[-1]['Close']
    portfolioStock = 0
    #buy the stock
    if principle > sharepriceInit:
        principle, cashflow, shares = buy(principle, sharepriceInit)
        portfolioStock = portfolioStock + shares
        
    #sell the stock
    if portfolioStock > 0:
        principle, cashflow, shares = sell(principle, sharepriceEnd, portfolioStock)

    #return the final principle
    successrate = 1
    return principle, successrate

def riskfree(pricedfChrono, principle, start, period=30):
    """
    For calculating scenarios where the strategy is holding risk-free bond.
    """
    successrate = 1
    return principle, successrate


def strategyTest(pricedf, principle, strategy=backtest, benchmark=buynhold, period=30, repeats = 100, verbose = False):
    """
    Repeatedly test a given strategy using random dates.

    pricedfChrono: price data of the stock in chronological order (oldest at top)
    strategy: strategy used to execute trades
    principle: initial starting money
    period: the number of period this strategy is employed over.
    repeats: number of repeated tests
    verbose: turn on debugging
    """
    pricedfChrono = clean.stock_data_reversetime(pricedf)
    #initialize the results
    testresults = np.array([])
    testresultsalpha = np.array([])
    srate = np.array([])
    #repeatedly test the strategy
    for i in range(repeats):
        #generate a random start date
        start = rng_date(pricedfChrono, period)

        #calculate the benchmark return, i.e. buy and hold
        buynhold, successbase = benchmark(pricedfChrono, principle, start, period)

        #calculate the return generated by the strategy
        trades, successrate = strategy(pricedfChrono, principle, start, period)
        #calculate excess return and alpha
        excessreturn = trades - buynhold
        alpha = excessreturn/principle

        #debugging
        if verbose:
            print(f"test {i}: benchmark result = {buynhold}")
            print(f"test {i}: trades result = {trades}")
            print(f"test {i}: excess return = {excessreturn}")
            print(f"test {i}: alpha = {alpha}")
            print(f"test {i}: success rate = {successrate}")
        
        #output the result
        testresults = np.append(testresults, excessreturn)
        testresultsalpha = np.append(testresultsalpha, alpha)
        srate = np.append(srate, successrate)
    
    
    #calculate the mean return
    mean = np.mean(testresults)
    meanA = np.mean(testresultsalpha)
    meansrate = np.mean(srate)
    
    #caclulate the median return
    median = np.median(testresults)
    medianA = np.median(testresultsalpha)
    
    #output results to terminal
    print(f"mean return = {mean}")
    print(f"median return = {median}")
    print(f"mean alpha = {meanA}")
    print(f"median alpha = {medianA}")
    print(f"strategy successrate = {meansrate}")

    #output results as an object
    results = test_results(mean, median, meanA, medianA, meansrate)

    return results
        

#
#pricedfChrono = pricedfChrono.reset_index(drop=True)

print("--- %s seconds ---" % (time.time() - start_time))