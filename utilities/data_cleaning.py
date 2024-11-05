import re
import pandas as pd
import pytz
from pathlib import Path
import os
import datetime as dt

#potential libs for finding dataframe types
#from pandas.api.types import is_float_dtype
#from pandas.api.types import is_integer_dtype

#======global variables=========#
nytz = pytz.timezone('US/Eastern') #new york timezone

#======clean data functions=====#
def clean_float(value):
    """
    Clean a given string so it returns float with at most 4 decimal places

    input:
        value: a string that may require cleaning
    output:
        cleaned_value: cleaned float
            OR when conversion failed:
        returns nan 

    by Chatgpt
    """
    #pass if it is already an float
    if isinstance(value, float):
        return round(value, 4) #force a 4 decimal place return
    
    # Use regex to keep only the first 4 decimal places
    match = re.match(r'^(\d+\.\d{1,4})', value)

    if match:
        cleaned_value = match.group(1)
        try:
            return float(cleaned_value)
        except ValueError:
            return float('nan')  # Return NaN if conversion fails
    else:
        return float('nan')  # Return NaN if no match is found

def clean_float_series(series):
    """
    apply clean_float function to a pandas series
    """
    return series.apply(clean_float)

def clean_integer(value):
    """
    Clean a given string so it returns an integer

    input:
        value: a string that may require cleaning
    output:
        cleaned_value: cleaned integer
            OR when conversion failed:
        returns nan 

    by Chatgpt
    """
    #pass if it is already an integer
    if isinstance(value, int):
        return value
    # Use regex to remove non-digit characters
    cleaned_value = re.sub(r'\D', '', value)
    try:
        return int(cleaned_value)
    except ValueError:
        return float('nan')  # Return NaN if conversion fails
    
def clean_integer_series(series):
    """
    apply clean_integer function to a pandas series
    """
    return series.apply(clean_integer)

#======dataframe standardisation functions=====#
def stock_data_process(pricedf, tz = nytz):
    """
    Process and clean the given stock data, so all of them are of the right type

    input:
        pricedf: price data of the stock

    return:
        pricedf: processed price data of the stock
    """
    #convert the time to nytz
    if pd.to_datetime(pricedf['Time'].iloc[0]).tz is None:
        #check if the data is timezone naive
        pricedf['Time'] = pd.to_datetime(pricedf['Time']).dt.tz_localize(tz)
    else:
        pricedf['Time'] = pd.to_datetime(pricedf['Time'], utc=True).dt.tz_convert(tz)

    #make sure all price data are in floats
    pricedf['Open'] = pricedf['Open'].apply(clean_float)
    pricedf['Close'] = pricedf['Close'].apply(clean_float)
    pricedf['High'] = pricedf['High'].apply(clean_float)
    pricedf['Low'] = pricedf['Low'].apply(clean_float)
    pricedf['Adj Close'] =  pricedf['Adj Close'].apply(clean_float)

    #make sure volume data is in integer
    pricedf['Volume'] = pricedf['Volume'].apply(clean_integer)

    #reset index to be compatible with iloc methods
    pricedf = pricedf.reset_index(drop=True)
    return pricedf

def stock_data_reversetime(pricedf):
    """
    reverse the time order of the given stock data
    usually for making them in chronological order
    input:
        pricedf: price data of the stock

    return:
        pricedfrev: time reversed price data of the stock
    """
    #reverse the order
    pricedfrev = pricedf.reindex(index=pricedf.index[::-1]) #reverse the order so oldest is at top
    #reset index to be compatible with iloc methods
    pricedfrev = pricedfrev.reset_index(drop=True)
    
    return pricedfrev

def historic_data_process(ticker, timeframe, tz = nytz):
    """
    Process and clean the given historic stock data csv, so all of them are of the right type

    input:
        ticker: ticker of the stock
        timeframe: timeframe we are interested
    return:
        none
        modifies the corresponding csv
    """
    #define the path to stock
    path = f'data/{ticker}'
    targetfile = f"{path}/{ticker}_{timeframe}.csv"
    targetpath = Path(targetfile)

    if targetpath.exists():
        #check if the data exist

        #grab the dataframe
        pricedf = pd.read_csv(targetfile)

        #clean the dataframe
        pricedf = stock_data_process(pricedf, tz)

        #create a new file with the updated dataframe
        output_file = 'temp.csv'
        pricedf.to_csv(output_file, index=False)
        os.replace('temp.csv', targetfile)



    else:
        print("No need for cleaning, target file does not exist")

#======dataframe extra info columns=====#
def add_change(pricedf):
    """
    Adds the change between two periods of a stock's data.

    input:
        pricedf: price data of the stock

    return:
        pricedf: pricedf with change and change %.
    """
    #check if the dataframe is in chronological order
    if pricedf['Time'][0] - pricedf['Time'][1] > dt.timedelta(0):
        chrono = False
    else:
        chrono = True

    #get change 
    if chrono:
        pricedf['Change'] = pricedf['Close'].diff()
        pricedf['Change%'] = pricedf['Change']*100/pricedf['Close']
    else:
        pricedf['Change'] = pricedf['Close'].diff(periods=-1)
        pricedf['Change%'] = pricedf['Change']*100/pricedf['Close']

    return pricedf.fillna(0)