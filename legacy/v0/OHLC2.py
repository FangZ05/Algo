"""Generate OHLC graph from csv data"""
import matplotlib.pyplot as plt
import mpl_finance as fi
import matplotlib.dates as mdates
from matplotlib import style
import pandas as pd

import matplotlib.ticker as mticker

dataDir = "data\\"
data = pd.read_csv(dataDir+'TSLA.csv', parse_dates = True, index_col = 0)
data.reset_index(inplace = True)

style.use('ggplot') #plot style

def ohlcData(df): #modify order of column to OHLC
    cols = ['Date','Open','High','Low','Close','Volume']
    df = df[cols]
    return df

def ohlcGraph(ticker): #Generate OHLC graph
    ticker = ticker.upper() #enforce uppercase
    data = pd.read_csv("data/"+'%s.csv'%ticker, parse_dates = True, index_col = 0)    
    data.reset_index(inplace = True)
    date = data[data.columns[1]]