# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 23:28:54 2024

@author: Fang
"""
import datetime as dt
import numpy as np
import pandas as pd

def return_dist(pricedfChrono, period=30):
    """
    Calculates the expected return distribution of a given period length

    pricedfChrono: price data of the stock in chronological order (oldest at top)
    period: number of period we look at the return

    """

    #turn period into time delta
    timedelta = dt.timedelta(days=period)

    #get the time df
    timeChrono = pricedfChrono['Time']

    #find the number of rows corresponding to the period
    end = timeChrono.iloc[0] + timedelta #find the ending time
    endloc = pricedfChrono[timeChrono>end].iloc[[0]].index[0] #find the index of above time
    endiloc = pricedfChrono.index.get_loc(endloc) #find the iloc of the above time

    #calculate return for each time
    lendf = timeChrono.shape[0] #length of dataframe
    results = np.array([])
    resultspercent = np.array([])
    for i in range(lendf):
        startprice = pricedfChrono['Close'].iloc[i]
        if i + endiloc >= lendf:
            endprice = pricedfChrono['Close'].iloc[-1]
        else:
            endindex = endiloc + i
            endprice = pricedfChrono['Close'].iloc[endindex]

        gains =  endprice - startprice
        gainspercent = gains/endprice
        results = np.append(results, gains)
        resultspercent = np.append(resultspercent, gainspercent)

    print(f"starting date: {timeChrono.iloc[0]}, period of {period}")
    print(f"average return per {period} days: {np.mean(resultspercent)}")
    print(f"median return per {period} days: {np.median(resultspercent)}")
    
    
    return results, resultspercent

def prev_max(pricedfChrono):
    """
    Calculates the previous all time high of the ticker
    """
    results = np.array([])
    currentmax = 0
    closeprice = pricedfChrono['Close']
    for i in closeprice:
        if i > currentmax:
            currentmax = i
        results = np.append(results, currentmax)
        
    df = pricedfChrono
    df['Previous Peak'] = pd.Series(results)
    return df

def stock_ratio(pricedf1, pricedf2, period=365):
    """
    Calculates the full OHLC movement ratio between two stocks
    
    input:
        pricedfChrono1: pricedf of first stock, organised in chronological order
        pricedfChrono2: pricedf of second stock, organised in chronological order
        
        (optional)
        
        period: how many days ago should be used as baseline. Default 1 year.
        
    return:
        ratio_df: the ratio data of the two stocks
    """

    
    #formulate the two df so they have the same end date
    current1 = pricedf1['Time'].iloc[0] #latest time of stock 1
    current2 = pricedf2['Time'].iloc[0] #latest time of stock 1
    
    
    #remove excess data
    if current1 > current2:
        pricedf1 = pricedf1[pricedf1['Time'] <= current2]
        current1 = current2
    else:
        pricedf2 = pricedf2[pricedf2['Time'] <= current1]
        current2 = current1
    
    #strip the data so there is only OHLC
    ohlc_columns = ['Open','High','Low','Close'] #price columns
    ohlc1 = pricedf1[ohlc_columns]
    ohlc2 = pricedf2[ohlc_columns]
    
    #get the data at the starting 
    start = current1 - dt.timedelta(days=period)
    startrow1 =  pricedf1[pricedf1['Time'] <= start].iloc[0][ohlc_columns]
    startrow2 =  pricedf2[pricedf2['Time'] <= start].iloc[0][ohlc_columns]
    
    #get the ratio at the start
    baseratio = startrow1/startrow2
    
    #calculate the ratio for each time, then normalise to the start value
    ratio_df = (ohlc1/ohlc2) * (1/baseratio) -1.0
    
    #convert data to float
    ratio_df = ratio_df.astype(float)
    
    #apply the time data
    ratio_df['Time'] = pricedf1['Time']
    
    #apply the volume data
    ratio_df['Volume'] = pricedf1['Volume'] + pricedf2['Volume']
       
    #organise the columns
    organised_columns = ['Time', 'Open','High','Low','Close', 'Volume']
    ratio_df = ratio_df[organised_columns]
    
    #remove nan values
    ratio_df = ratio_df.dropna()
    
    return ratio_df
    
def stock_ratio_close(pricedf1, pricedf2, period=365):
    """
    Calculates the movement ratio between two stocks using their closing price

    pricedfChrono1: pricedf of first stock, organised in chronological order
    pricedfChrono1: pricedf of second stock, organised in chronological order

    period: how many days ago should be used as baseline

    """

    #formulate the two df so they have the same end date
    current1 = pricedf1['Time'].iloc[0] #latest time of stock 1
    current2 = pricedf2['Time'].iloc[0] #latest time of stock 1
    

    #remove excess data
    if current1 > current2:
        pricedf1 = pricedf1[pricedf1['Time'] <= current2]
        current1 = current2
    else:
        pricedf2 = pricedf2[pricedf2['Time'] <= current1]
        current2 = current1
    
    #get the data at the starting 
    start = current1 - dt.timedelta(days=period)
    startrow1 =  pricedf1[pricedf1['Time'] <= start].iloc[0]
    startrow2 =  pricedf2[pricedf2['Time'] <= start].iloc[0]
    
    #get the ratio at the start
    baseratio= startrow1['Close']/startrow2['Close']
    
    #calculate the ratio for each time, then normalise to the start value
    ratio = pricedf1['Close']/pricedf2['Close'] * (1/baseratio)-1
    
    return ratio
    