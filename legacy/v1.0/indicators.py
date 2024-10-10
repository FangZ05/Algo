#market analysis libraries
from contextvars import copy_context
from tkinter import X
import yfinance as yf
#scientific libraries
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

import scipy.stats as stats
#os manipulation libraries
from pathlib import Path
import os
import csv
import datetime as dt
#custom libraries
import pythonfunct as h 
'''make sure a directory named "data" exist'''


#plot the volume denity profile
def volprof(axs, pricedf, graphSize):
    ax2 = axs.twiny() #share the y axis
    #price width of each volume density bar
    binwidth=min(pricedf['Close'].iloc[-1]*0.005 ,2)
    #define variables
    close = pricedf['Close'][-graphSize:]
    volume = pricedf['Volume'][-graphSize:]
    ax2.hist(close, 
             weights=volume, #Volume profile
             bins=np.arange(min(close), max(close) + binwidth, binwidth),
             orientation='horizontal',
             alpha = 0.25)
    ax2.invert_xaxis()

#calculate intraday changes, percentage
def chng_intraday(pricedf):
    open = pricedf['Open']
    close = pricedf['Close']
    return (close - open)/open*100 #percentage calculated as change/current open

#calculate overnight changes, percentage
def chng_overnight(pricedf):
    open = pricedf['Open']
    close = pricedf['Close']
    size = len(open)
    changep = pd.Series(0, index=range(size), dtype=float) #series for percent change
    change = 0 
    for i in range(1, size):
        copen = open[i]
        pclose = close[i-1]
        change =  copen - pclose
        changep[i] = (change/pclose)*100 #percentage calculated as change/prev. close
    return changep

def mean_moving(period, axs, pricedf, graphSize):
    #get the closing price
    price = pricedf['Close']
    #get the moving average
    size = len(price)
    
    meanmoving = pd.Series(np.nan, index=range(size), dtype=float)
    for i in range (period, size+1):
        meanmoving[i-1] = price[i-period:i].mean()
    
    #plot the data
    x = np.arange(0,graphSize)
    axs.plot(x, meanmoving[-graphSize:], linewidth = 0.7, label = period)
    axs.legend(loc="upper right")
    return meanmoving