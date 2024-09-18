"""AlgoTrading 1"""

import datetime as dt
from pandas.plotting import register_matplotlib_converters
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
from matplotlib import style
import pandas as pd
#import pandas_datareader.data as web

style.use('ggplot')

# ======grab data from web=======================================================================
# start = dt.datetime(2000,1,1)
# end = dt.datetime(2019,4,20)
# 
# tsla = web.DataReader('NASDAQ:TSLA','yahoo',start, end)
# df.to_csv('tsla.)
# =============================================================================

tsla = pd.read_csv('tsla.csv', parse_dates = True, index_col = 0)


#Resampling#

tsla_ohlc = tsla['Adj Close'].resample('1W').ohlc()
tsla_volume = tsla['Volume'].resample('1W').sum()

tsla_ohlc.reset_index(inplace = True)

tsla_ohlc['Date'] = tsla_ohlc['Date'].map(mdates.date2num)


print(tsla_ohlc.head())

#generate plot#

ax1 = plt.subplot2grid((6,1),(0,0), rowspan=5, colspan = 1)
ax2 = plt.subplot2grid((6,1),(5,0), rowspan=1, colspan = 1, sharex=ax1)

ax1.xaxis_date()

candlestick_ohlc(ax1, tsla_ohlc.values, width=2, colorup = 'g')
ax2.fill_between(tsla_volume.index.map(mdates.date2num), tsla_volume.values, 0)

plt.show()