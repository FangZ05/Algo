#yahoo finance lib
import yfinance as yf

#pandas lib
import pandas as pd

#sys libs
from pathlib import Path
import os
import csv
import datetime as dt
import pytz

'''
library for downloading yfinance data into csv files.
Also for downloads basic infos of the stock.
'''

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
            f.write(f"{key} : {value} \n")
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
def getTickerData(ticker, timeframe, update = True,  p='data/', tz = "Australia/Brisbane"):
    ''''Get the data for specified ticker.
        ticker: stock's ticker symbol
        update: Force update. Default true.
        p: pathway to data folder.'''
    #========================================================#

    #define data as found using yfinance
    tdata = yf.Ticker(ticker)

    #specify file path
    path = p + ticker
    filepath = Path(path) 

    #get the current time
    localtz = pytz.timezone(tz) 
    now = dt.datetime.now(localtz)

    #========================================================#


    #define the maximum look back period for each timeframe as per yfinance package
    timeframe_to_maximum = { #defines the maximum period for each timeframe
        '1m' : '7d',
        '2m' : '60d',
        '5m' : '60d',
        '15m' : '60d',
        '30m' : '60d',
        '90m' : '60d',
        '60m' : '730d',
        '1h' : '730d',
        '1d' : 'max',
        '5d' : 'max',
        '1wk' : 'max',
        '1mo' : 'max',
        '3mo' : 'max'
    }
    if timeframe in timeframe_to_maximum: #match the timeframe to period
        maximum = timeframe_to_maximum[timeframe]
    else:
        raise ValueError("Timeframe error: Invalid timeframe value.")

    #convert the given maximums into timedelta
    
    maximum_to_timedelta = {
         '7d' : dt.timedelta(days=6, hours = 23, minutes = 50),
         '60d' : dt.timedelta(days=59, hours = 23),
         '730d' : dt.timedelta(days=729, hours=23),
         'max' : dt.timedelta(years=99)
    }

    '''maximum_to_timedelta = {
         '7d' : dt.timedelta(days=7),
         '60d' : dt.timedelta(days=60),
         '730d' : dt.timedelta(days=730),
         'max' : dt.timedelta()
    }'''
    if maximum in maximum_to_timedelta: #match the maximum to timedelta
        maxtimedelta = maximum_to_timedelta[maximum]

    #get the maximum start time
    maxstart = now - maxtimedelta
    #========================================================#

    #function to download data
    def getdata(startdate, enddate):
        #get price data and save as csv
        thisdata = yf.download(ticker, start = startdate, end = enddate, interval = timeframe)

        thisdata = thisdata.reindex(index=thisdata.index[::-1]) #reverse the order so latest is at top
        thisdata = thisdata.reset_index(level=0) #index the data by number instead of date
        thisdata = thisdata.rename(columns={thisdata.columns[0]: 'Time'}) #rename the date column

        return thisdata
    
    def getdataperiod(time):
        #get price data and save as csv
        thisdata = yf.download(ticker, period = time, interval = timeframe)

        thisdata = thisdata.reindex(index=thisdata.index[::-1]) #reverse the order so latest is at top
        thisdata = thisdata.reset_index(level=0) #index the data by number instead of date
        thisdata = thisdata.rename(columns={thisdata.columns[0]: 'Time'}) #rename the date column

        return thisdata
    
    #========================================================#
    #get target file
    targetfile = f"{path}/{ticker}_{timeframe}.csv"
    targetpath = Path(targetfile)

    #check if the ticker is new
    #if ticker is not new
    if filepath.exists():
        #update the data if it already exists
        if targetpath.exists():
            if update:


                #get the last datapoint collected
                latest = pd.read_csv(targetfile, nrows = 1)
                lastupdate = pd.to_datetime(latest['Time'][0])

                #get time since last update
                sinceupdate = now - lastupdate

                #check if last update exceeds maximum for given timeframe and grab data from yfinance
                if sinceupdate >= maxtimedelta:
                    data = getdataperiod(maximum)
                else:
                    data = getdata(lastupdate, now)

                #convert updated portion of the data into csv
                data.to_csv('update.csv', index=False)

                #check for redudant update
                lastdata = pd.to_datetime(data['Time'][0])
                if lastdata == lastupdate:
                    pass
                else:
                    #update the data using chunks
                    CHUNK_SIZE = 100000 # Number of Rows
                    output_file = 'temp.csv'

                    first_one = True #for skipping header
                    for csv_file_name in ['update.csv', targetpath]:

                        if not first_one: # if it is not the first csv file then skip the header row (row 0) of that file
                            skip_row = [0]
                        else:
                            skip_row = []

                        chunk_container = pd.read_csv(csv_file_name, chunksize=CHUNK_SIZE, skiprows = skip_row)
                        for chunk in chunk_container:
                            chunk.to_csv(output_file, mode="a", index=False) #combine files
                        first_one = False

                    #replace original with updated file
                    os.replace('temp.csv', targetfile)
                #remove temporary file
                os.remove('update.csv')

        #otherwise treat symbol as if it is new
        else: 
            #get info of stock
            getinfo(ticker, p)

            #get price data of maximum period
            data = getdataperiod(maximum)
            data.to_csv(targetfile, index=False) #write to csv

    #if symbol is new
    else:    
        #make directory for the ticker
        os.mkdir(path)

        #get info of stock
        getinfo(ticker, p)

        #get price data of maximum period
        data = getdataperiod(maximum)
        data.to_csv(targetfile, index=False) #write to csv


