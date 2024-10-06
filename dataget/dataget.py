"""
General functions for grabbing data.
"""


from pathlib import Path

if __name__ == '__main__':
    import sys
    import os
    #mimics relative import when run as a script
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)


    
import yfinData as ydata
import pandas as pd
import utilities.data_cleaning as clean
from utilities.fileManagement import find_project_root
import csv

root_dir = find_project_root(project_name='algo')+'/' #get the root directory of this project

def stock_data_get(ticker, timeframe, update = False, chrono = False, period=None):
    """get the local stock data as a dataframe
    
    ticker: ticker of the stock
    timeframe: timeframe that was interested
    period: number of datapoints are requested
    
    Special note: local df are stored with latest data at the top
    """
    
    #define the path to stock
    path = root_dir+f'data/{ticker}'
    targetfile = Path(f"{path}/{ticker}_{timeframe}.csv")
    
    #always update if the file does not exist
    if not targetfile.exists(): 
        update = True

    #check if update is needed
    if update:
        ydata.getTickerData(ticker, timeframe)
        
    #get the dataframe
    pricedf = pd.read_csv(targetfile, nrows = period)

    #ask if we want the stock to be arranged in chronological order
    if chrono:
        pricedf = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so oldest is at top
    
    #standardize the data using cleaning module
    pricedf = clean.stock_data_process(pricedf)
    
    return pricedf

#same as tdata.info, but local
def stock_info_getLocal(ticker, p=root_dir+'data'):
    #get path to file
    path = f"{p}/{ticker}"

    #open .csv with dictionary reader
    with open(f"{path}/{ticker}_info.csv", mode='r', encoding='UTF-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            info = row
    #return a dictionary
    return info