import yfinance as yf

ticker = 'MSFT'

tickerData = yf.Ticker(ticker)

tickerDF =  tickerData.history(period='1d', interval = "1m")





#def getdata(ticker):
    
    