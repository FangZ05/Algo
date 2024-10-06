"""
All related information about reversion strategy for 
vix, 30 day forward volatility index of SnP500

Theory: The vix will return to around its median value following a run up

idea:
    find the overall median
    construct a trailing median to see the trend

"""

if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

#=====================#

#=====================#



if __name__ == '__main__':
    #run as a script

    ticker = "^VIX"
    #define the path to stock
    path = f'data/{ticker}'
    targetfile = f"{path}/{ticker}_{timeframe}.csv"
    
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