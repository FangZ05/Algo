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

from dataget.dataget import stock_data_get

#function to calculate the quantile of a value within the series
from scipy.stats import percentileofscore

#=====================#

#=====================#



if __name__ == '__main__':
    #run as a script
    
    #use daily 
    ticker = "^VIX"
    timeframe = '1d'
    
    vixdf = stock_data_get(ticker, timeframe)
    vix = vixdf['Close']
    
    