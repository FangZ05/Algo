#yahoo finance lib
import yfinance as yf

#sys libs
from pathlib import Path
import os
import csv
import datetime as dt


#function to download stock info
def getinfo(ticker, p='data/'):
    #get data from yfinance
    tdata = yf.Ticker(ticker)

    #specify file path
    path = p + ticker
    filepath = Path(path)

    #cache the stock info as variable
    info = tdata.info
    #write the info page
    with open(path+'/{} info.txt'.format(ticker), 'w', encoding='UTF8') as f:
        for key, value in info.items():
            f.write("{}:{} \n".format(key, value))
        f.close()
    #write the info page to csv readable format 
    with open(path+'/{} info.csv'.format(ticker), 'w', encoding='UTF8') as f:
        writer = csv.DictWriter(f, info.keys())    
        writer.writeheader()
        writer.writerow(info)
        f.close()
    return info


#same as tdata.info, but local
def getInfoLocal(ticker, p='data/'):
    #get path to file
    path = p + ticker
    #open .csv with dictionary reader
    with open(path+"/{} info.csv".format(ticker), mode='r', encoding='UTF-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            info = row
    #return a dictionary
    return info

#specify file path for output
def getTickerData(ticker, update = False, updtfreq = 1,  p='data/'):
    ''''Get the data for specified ticker.
        ticker: stock's ticker symbol
        updtfreq: specify when data is old enough for update. Unit in days.
        update: Force update. Default false.
        p: pathway to data folder.'''

    #define data as found using yfinance
    tdata = yf.Ticker(ticker)

    #specify file path
    path = p + ticker
    filepath = Path(path) 
    
    #function to download data
    def getdata():
        #get price data
        histdaily = yf.download(ticker, period = "max", interval='1wk')
        histdaily = histdaily.reset_index(level=0)
        histdaily = histdaily.rename(columns={histdaily.columns[0]: 'Time'})
        histdaily.to_csv(path + '/{}_daily.csv'.format(ticker))
        '''
        histhourly = yf.download(ticker, period = "730d", interval='1h' )
        histhourly = histhourly.reset_index(level=0)
        histhourly = histhourly.rename(columns={histhourly.columns[0]: 'Time'})
        histhourly.to_csv(path + '/{}_hourly.csv'.format(ticker))
        '''
    #check if the ticker is new
    #if ticker is not new
    if filepath.exists():
        #get today's date
        date = dt.datetime.today()
        #today = date.strftime("%Y-%m-%d")

        #get last modifited time of the data
        time = os.path.getmtime(path + '/{}_daily.csv'.format(ticker))
        lastmod = dt.datetime.fromtimestamp(time)

        #get update frequency
        freq = dt.timedelta(days=updtfreq)
        #check if update is required by checking last modified date
        #update if data is too old
        if date - lastmod > freq:
            update = True

        #update the data
        if update:
            getdata()

    #if symbol is new
    else:    
        #make directory for the ticker
        os.mkdir(path)
        #get info of stock
        getinfo(ticker, p)
        #get price data
        getdata()


