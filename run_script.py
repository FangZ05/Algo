from options.optionsBlackScholes import options
from strategies.optionsStrategies import *

from dataget.dataget import*
import utilities.data_cleaning as clean
import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
#function to calculate the quantile of a value within the series
from scipy.stats import percentileofscore

from technicals.correlation import corr

from copy import deepcopy
ticker = 'iwm'
timeframe = '1d'
iwm = stock_data_get('iwm', timeframe)
qqq = stock_data_get('qqq', timeframe)
spy = stock_data_get('spy', timeframe)

rty = stock_data_get('rty=f', timeframe)