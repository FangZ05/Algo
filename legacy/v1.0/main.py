#%matplotlib auto
"""
Main script of the trading alogrithm
All time in GMT
"""
#library of functions for trading
import indicators as ind
import yfinData as ydata
import charting as chart
import optionsBlackScholes as options
import optionsStrats as strats
import dividends as div
import fixed_income as bond
import misc

#market analysis libraries
import yfinance as yf
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

#os manipulation libraries
from pathlib import Path
import os
import csv
import datetime as dt

#Other useful libraries
import webbrowser #web browser interaction
#from tempfile import NamedTemporaryFile


#global variables

#get ticker
#ticker = input("Enter Stock symbol")
ticker = "QQQ"
ticker = ticker.upper()

#limit the size of dataset. Each day has ~7 hours.
days = 120
period = 7 #7 for hourly, 1 for daily
    
#path to stock data
path = 'data/{}'.format(ticker)

update = 1
if update == 1:
    update1 = True
else:
    update1 = False
   
#=================Run Program=======================#
#get data using yfinance
ydata.getTickerData(ticker, update1)
    
#get stock info
tdata = yf.Ticker(ticker)
info = ydata.getInfoLocal(ticker)

#get today's date at NY time
date = dt.datetime.today() - dt.timedelta(hours=15)
datestr = date.strftime("%Y-%m-%d")
    
#epst = float(info['trailingEps'])
#epsf = float(info['forwardEps'])
#sharecount = int(info['sharesOutstanding'])
    
#datetime format
#dateparse = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

#pricedf = pd.read_csv(path+'/{}_hourly.csv'.format(ticker))
pricedf = pd.read_csv(path+'/{}_daily.csv'.format(ticker))
#, parse_dates = ['Time'], date_parser=dateparse
lastprice = pricedf['Close'].iloc[-1]
    
#remove utc label (hourly only)
pricedf['Time'] = pd.to_datetime(pricedf['Time'].map(lambda x: x[:-6]))
pricedf = pricedf.drop(pricedf.columns[0],axis=1)
#pricedf = pricedf[-days*period:]
#pricedf = pricedf.reset_index()

#setup the browser
#firefox_path = "C:\Program Files\Mozilla Firefox\firefox.exe"
#webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))
def df_window(df):
#show large pandas table in html
    filename = "temp/optionsChain.html"
    with open(filename, 'w') as f:
    #with NamedTemporaryFile(mode = 'w', delete=False, suffix='.html') as f:
        df.to_html(f)
    webbrowser.open('file://' + os.path.realpath(filename))


def updateTicker (stock):
    #force update a ticker's data
    ydata.getTickerData(stock, True)

#get the option chain for a specific date
def optionsChain(exp):
    opt = tdata.option_chain(exp)
    
    #specify type for each options
    calls = opt.calls
    calls['type'] = 'call'
    puts = opt.puts
    puts['type'] = 'put'
    frames = [calls, puts]
    
    #combine the two dataframes
    opt = pd.concat(frames)
    opt['expirationDate'] = exp
    
    #remove unnecessary columns
    opt = opt.drop(['lastTradeDate', 'contractSize', 'inTheMoney', 
                    'currency', 'percentChange','change'], axis=1)
    
    return opt

def optionsAll():
    #get a list of expiration dates
    exps = tdata.options
    optsframe = []
    for e in exps:
        optsframe.append(optionsChain(e))
    opts = pd.concat(optsframe, ignore_index=True)
    return opts
        
def consecutives (t, df = pricedf, ud = "up"):
    #number of consecutive days the stock is up/down
    #t: number of consecutive days
    #df: the stock's dataframe
    #ud: "up" or "down"
    consec = 0
    num = 0
    if ud == "up":
        ind = 1
    else:
        ind = -1
    diff = df['Open'] - df['Close']
    for i in diff:
        if (i*ind) > 0:
            consec += 1
        if (i*ind) <= 0:
            consec = 0
        if consec >= t:
            num +=1
    return num

def graph():
    if pricedf.empty:
        print("No data avaliable.")
        return 1

    #graph parameters
    graphSize = days*period
    dfgraph = pricedf[-graphSize:]
    dfgraph = dfgraph.reset_index()
    
    
    #make candlestick chart. axs will be the plot object.
    axs = chart.candlestickPlot(ticker, dfgraph)
    
    #ind.volprof(axs, pricedf, graphSize) #add volume profile
    ind.mean_moving(26, axs, pricedf, graphSize)
    ind.mean_moving(50, axs, pricedf, graphSize)
    ind.mean_moving(100, axs, pricedf, graphSize)
    ind.mean_moving(200, axs, pricedf, graphSize)
    
    scale = 1.5
    #f = chart.zoom_factory(axs,base_scale = scale)
    return 0
    
def main():
    return 0



#options parameters
exps = tdata.options

#get the options chain
expr = exps[8]
exprs = '2023-03-20'
chains = optionsChain(expr)

S = lastprice # current price
K1 = 296
K2 = 180

p = "put"
c = "call"

op1 = chains.loc[(chains["strike"] == K1) &(chains["type"] == p)]
op2 = chains.loc[(chains["strike"] == K2) &(chains["type"] == p)]

manual = 1
if manual == 1:
    #sigma1 = 0.604
    #sigma2 = 0.617
    sigma1 = 0.504
    sigma2 = 0.517
else:
    sigma1 = op1.impliedVolatility.iloc[0]
    sigma2 = op2.impliedVolatility.iloc[0]

sigma = 0.26
r = 0.0475
q = div.divYield(tdata, lastprice)

test = '2023-10-05'
exprdate = dt.datetime.strptime(exprs, "%Y-%m-%d") + dt.timedelta(hours=16)
tdelta = abs(date - exprdate)
offset = -0.5
T = tdelta.days + tdelta.seconds/86400

op = options.price(p, lastprice, K1, T-0*offset, r, sigma, q)
#res = 1
res = main()
if res == 0:
    print("Progam executed successfully.")
else:
    print("Program exited with error.")
    