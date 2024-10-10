import yfinance as yf
import datetime as dt
from pandas.plotting import register_matplotlib_converters
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_finance as fi
import matplotlib.dates as mdates
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.ticker as mticker
import ohlc


dataDir = "data\\"

def dataFetch(ticker,period='3mo',interval='1h', country='', ext = False):
    ticker = ticker.upper()
    data = yf.Ticker("%s"%ticker)
    hist = data.history(period="%s"%period, interval="%s"%interval, prepost= ext)
    hist.to_csv(dataDir+"%s.csv"%ticker)

def showStock(ticker):
    dataFetch(ticker, interval = '1m', period = '3d')
    ohlc.ohlcGraph(ticker, dataDir)    