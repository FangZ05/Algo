if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

import numpy as np
from scipy.stats import norm
from fundamentals.riskFreeRate import risk_free_rate

#easy function access
N = norm.cdf

rf_rates = risk_free_rate()/100

def d_calc(S, K, T, sigma, r = rf_rates, q=0):
    '''
    Calculates the d function of Black Scholes Model.

    S: underlying price.
    K: options strike price.
    T: Time until expiry (years).
    r: risk free rates. Default 3mo T-bill yield.
    sigma: implied volatility of the options.
    q: dividend of underlying.

    '''
    #limit T so you do not get divide by zero error
    if T < 0.000001:
        T = 0.000001
    d1 = (np.log(S/K) + (r - q + sigma**2/2)*T) /(sigma*np.sqrt(T))
    d2 = d1 -  (sigma*np.sqrt(T))
    return d1, d2


#calculate the options' price
def price(cp, S, K, T, sigma, r = rf_rates, q=0):
    '''
    Calculates the price of options.

    cp: calls or puts.
    S: underlying price.
    K: options strike price.
    T: Time until expiry (days).
    r: risk free rates. Default 3mo T-bill yield.
    sigma: implied volatility of the options.
    q: dividend of underlying.
    '''
    cp = cp.upper() #turn everything into upper case
    tte = T/365.0 #time in years
    d = d_calc(S, K, tte, sigma, r = r, q=0)
    d1 = d[0]
    d2 = d[1]
    if cp == "C" or cp == "CALL" or cp == "CALLS":
        return S * N(d1) - K * np.exp(-r*tte)* N(d2)
    elif cp == "P" or cp == "PUT" or cp == "PUTS":
        return K*np.exp(-r*tte)*N(-d2) - S*N(-d1)
    else:
        print("Error: not a put or call.")

#calculate the delta of options
def delta(cp, S, K, T, sigma, r = rf_rates, q=0):
    '''
    Calculates the Delta of options

    cp: calls or puts
    S: underlying price
    K: options strike price
    T: Time until expiry (days)
    r: risk free rates
    sigma: implied volatility of the options
    q: dividend of underlying
    '''
    
    cp = cp.upper() #turn everything into upper case
    tte = T/365.0 #time in years
    #calculate d1

    d = d_calc(S, K, T, r, sigma, q)
    d1 = d[0]
    d2 = d[1]
    #import gaussian cdf
    if cp == "C" or cp == "CALL" or cp == "CALLS":
        return N(d1)
    if cp == "P" or cp == "PUT" or cp == "PUTS":
        return N(d1) -1
    else:
        print("Error: not a put or call.")

def impVol():
    return 1


