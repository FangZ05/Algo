import datetime as dt
import pytz
import pandas as pd
import numpy as np
import pandas_ta as ta
import utilities.data_cleaning as clean
import pytz
import datetime as dt
import pandas as pd

#=====global variables=====#
nytz = pytz.timezone('US/Eastern')
tz = "Australia/Brisbane"
localtz = pytz.timezone(tz)
now = dt.datetime.now(localtz)



#======common functions=====#
def long(principle, price, shares=None):
    """
    Calculates the necessary parameters when you buy a stock
    """
    if (shares==None) or ((price*shares)>principle):
        shares = principle//price
    cashflow = -1 * shares * price
    principle = principle + cashflow
    return principle, cashflow, shares

def short(principle, price, shares=None):
    """
    Calculates the necessary parameters when you buy a stock
    """
    if (shares==None) or ((price*shares)>principle):
        shares = -principle//price
    cashflow = -1 * shares * price
    principle = principle + cashflow
    return principle, cashflow, shares
    
def close(principle, price, shares):
    """
    Calculates the necessary parameters when you sell a stock
    """
    cashflow = price*shares
    principle = principle + cashflow
    return principle, cashflow, shares