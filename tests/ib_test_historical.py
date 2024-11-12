from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd

import threading
import time

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.data = [] #Initialize variable to store candle

	def historicalData(self, reqId, bar):
		print(f'All data: {bar}')
		self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
		
def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7497, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
eurusd_contract = Contract()
eurusd_contract.symbol = 'TSLA'
eurusd_contract.secType = 'STK'
eurusd_contract.exchange = 'SMART'
eurusd_contract.currency = 'USD'

#Request historical candles
app.reqHistoricalData(1, eurusd_contract, '', '100 D', '1 day', 'ADJUSTED_LAST', 0, 2, False, [])

time.sleep(2) #sleep to allow enough time for data to be returned

#Working with Pandas DataFrames

df = pd.DataFrame(app.data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
#df['Time'] = pd.to_numeric(df['Time'], errors = 'ignore')
#df['Time'] = pd.to_datetime(df['Time'], unit='s') 
df.to_csv('TSLA_1d.csv')  

print(app.data[0])


app.disconnect()