import pandas as pd
import pytz
import requests
import numpy as np
from lightweight_charts import Chart
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()

'''
api_key = 'RbllAOb20LDwG1q1FGUtbaK6fwuhii68'
hist_json = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/AAPL?apikey={api_key}').json()

hist_df = pd.DataFrame(hist_json['historical']).drop('label', axis = 1)
hist_df = hist_df.iloc[::-1].reset_index().drop(['index','adjClose'], axis = 1)
hist_df.date = pd.to_datetime(hist_df.date)
hist_df = hist_df.iloc[:,:6].iloc[-365:]
hist_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']

hist_df.tail()
'''

nytz = pytz.timezone('US/Eastern')
ticker = "IWM"
timeframe = '1d'
path = f'data/{ticker}'
filepath = f"{path}/{ticker}_{timeframe}.csv"

pricedf = pd.read_csv(filepath, nrows=10)
pricedf=pricedf.drop([0])
pricedf = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so latest is at top
#pricedf['Time'] = pd.to_datetime(pricedf['Time'], utc=True).dt.tz_convert(nytz).dt.tz_convert(None)
#pricedf = pricedf.drop(columns=['Adj Close'])
#pricedf = pricedf.rename(columns={'Time':'time', 'Open': 'open', 'Close':'close','High':'high','Low':'low','Volume':'volume'}) #rename the date column
ticker = ticker.upper() #converts ticker to uppercase letters



