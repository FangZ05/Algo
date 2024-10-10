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
    date = date.map(mdates.date2num)
    #read data and convert date to numbner
    
    date =data[data.columns[1]]

# =============================================================================
#     count = 1
#     t = 0
#     
#     for i in range(0,len(date)):
#         if date[i] == date[i+1]:
#             count +=1
#         else:
#             t = date[i+1]-date[i]
#             break
#     width = 5*t/count
#     
#     
# =============================================================================
    width = 0.75
    
    ax1 = plt.subplot2grid((6,1),(0,0), rowspan=5, colspan = 1)
    ax2 = plt.subplot2grid((6,1),(5,0), rowspan=1, colspan = 1, sharex=ax1)
    #generate plot with volume


    step = int(len(data)/10) #intervals between major x tick
    x_ax =[]
    time = date.map(mdates.num2date).apply(lambda x: x.strftime("%m-%d"))
    #x tick labels
    
    for n,i in enumerate(time):
        if n%step==0:
            x_ax.append(i)
        else:
            x_ax.append('')
    #generate a set of x labels
            
    ax1.set(xticks=range(len(data)), xticklabels=x_ax, title = ticker)
    #set x labels
    
    fi.candlestick2_ohlc(ax1, data['Open'],data['High'],data['Low'],data['Close'], 
                         width=width, colorup = 'g')
    ax2.bar(data.index,data['Volume'], color = 'b')
    #generate OHLC and volume graph
    
    ax1.tick_params(axis='x', which='both', bottom=False, top=False)
    #remove excess features
    
    plt.show()