"""AlgoTrading 1"""

import datetime as dt
from pandas.plotting import register_matplotlib_converters
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

def ohlcData(df):
    cols = ['Date','Open','High','Low','Close','Volume']
    df = df[cols]
    return df

style.use('ggplot')

# ======grab data from web=============================================
# start = dt.datetime(2000,1,1)
# end = dt.datetime(2019,4,20)

# tsla = web.DataReader('NASDAQ:TSLA','bloomberg',start, end)
# df.to_csv('tsla.csv')
# ================================================================

dataDir = 'data\\'

tsla = pd.read_csv(dataDir+'tsla.csv', parse_dates = True, index_col = 0)



#Resampling#

tsla_ohlc = tsla['Adj Close'].resample('1W').ohlc()
tsla_volume = tsla['Volume'].resample('1W').sum()

tsla_ohlc.reset_index(inplace = True)
tsla.reset_index(inplace = True)
#tsla['Date']=tsla['Date'].map(mdates.date2num)

tsla_ohlc['Date'] = tsla_ohlc['Date'].map(mdates.date2num)


print(tsla_ohlc.head())

#generate plot#

ax1 = plt.subplot2grid((6,1),(0,0), rowspan=5, colspan = 1)
ax2 = plt.subplot2grid((6,1),(5,0), rowspan=1, colspan = 1, sharex=ax1)
ax1.xaxis_date()
# 
candlestick_ohlc(ax1, tsla_ohlc.values, width=.7, colorup = 'g')
ax2.bar(tsla_volume.index.map(mdates.date2num),tsla_volume.values, width=5)
#ax2.fill_between(tsla_volume.index.map(mdates.date2num), tsla_volume.values, 0, color = 'b')
# # 
plt.show()
# 
# =============================================================================
