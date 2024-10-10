#yahoo finance lib
import yfinance as yf

#data cleaning lib
import utilities.data_cleaning as clean
#pandas lib
import pandas as pd

#sys libs
from pathlib import Path
import os
import csv
import datetime as dt
import pytz
from utilities.fileManagement import find_project_root

'''
library for downloading yfinance data into csv files.
Also for downloads basic infos of the stock.
'''
root_dir = find_project_root(project_name = 'algo')+'/' #get the root directory of this project

#function to download stock info
def stock_info_get(ticker, p=root_dir+'data/'):
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


#specify file path for output
def getTickerData(ticker, timeframe, update = True,  p=root_dir+'data/', tz = "Australia/Brisbane"):
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

    #get the New York timezone for NYSE
    nytz = pytz.timezone('US/Eastern')

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
         'max' : dt.timedelta(days=40000)
    } #special note: added a small buffer to prevent rounding bugs

    if maximum in maximum_to_timedelta: #match the maximum to timedelta
        maxtimedelta = maximum_to_timedelta[maximum]

    #get the maximum start time
    maxstart = now - maxtimedelta
    #========================================================#

    #function to download data
    def getdata(startdate, enddate):
        #get price data and save as csv
        thisdata = yf.download(ticker, start = startdate, end = enddate, interval = timeframe)
        
        thisdata = thisdata.reindex(index=thisdata.index[::-1])             #reverse the order so latest is at top
        thisdata = thisdata.reset_index(level=0)                            #index the data by number instead of date
        thisdata = thisdata.rename(columns={thisdata.columns[0]: 'Time'})   #rename the date column for consistent format

        #standardize the data, time in nytz, prices in 4 decimal places, volumne in integer
        thisdata = clean.stock_data_process(thisdata) 

        #print the updated data for debugging purpose
        print("\nupdated data:")
        print(thisdata)
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

                #check if lastupdate has timezone info
                if lastupdate.tzinfo is None or lastupdate.tzinfo.utcoffset(lastupdate) is None:
                    lastupdate = nytz.localize(lastupdate)
                
                print(f"last update: {lastupdate}")

                #get time since last update
                sinceupdate = now - lastupdate

                #check if last update exceeds maximum for given timeframe and grab data from yfinance
                if sinceupdate >= maxtimedelta:
                    data = getdata(maxstart, now)
                else:
                    data = getdata(lastupdate, now)

                #check for redudant update
                if data.empty:
                    #ignore all if there is no update
                    pass
                else:
                    #get the time range of the update data & standardize to nytz
                    updatehead = pd.to_datetime(data['Time'].iloc[0])
                    if updatehead.tzinfo is None or updatehead.tzinfo.utcoffset(updatehead) is None:
                        updatehead = nytz.localize(updatehead)
                    updatetail = pd.to_datetime(data['Time'].iloc[-1])
                    if updatetail.tzinfo is None or updatetail.tzinfo.utcoffset(updatetail) is None:
                        updatetail = nytz.localize(updatetail)

                    if updatehead == lastupdate:
                        #check if there is only one update
                        pass
                    else:
                        #remove possible duplicates
                        dropfirst = False #for dropping bad data
                        if updatetail == lastupdate:
                            if latest['Volume'][0] < data['Volume'].iloc[-1]:
                                #check for incomplete data. i.e. data collected before the interval was finished
                                dropfirst = True
                            else:
                                data = data.drop(data.tail(1).index)

                        #convert updated portion of the data into csv
                        data.to_csv('update.csv', index=False)

                        #update the data using chunks
                        CHUNK_SIZE = 100000 # Number of Rows
                        output_file = 'temp.csv'

                        first_one = True #for skipping header
                        for csv_file_name in ['update.csv', targetpath]:

                            if first_one: 
                                #if it is the first csv file then keep the header row (row 0) of that file
                                skip_row = []
                            else:
                                #otherwise remove header
                                skip_row = [0]
                            
                            if dropfirst:
                                #if we want to skip the first entry of the existing file
                                if csv_file_name == targetpath:
                                    skip_row = [0, 1]
                                    dropfirst = False
                                    print("test: dropfirst triggered")



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
            stock_info_get(ticker, p)

            #get price data of maximum period
            data = getdata(maxstart, now)
            data.to_csv(targetfile, index=False) #write to csv

    #if symbol is new
    else:    
        #make directory for the ticker
        os.mkdir(path)

        #get info of stock
        stock_info_get(ticker, p)

        #get price data of maximum period
        data = getdata(maxstart, now)
        data.to_csv(targetfile, index=False) #write to csv

