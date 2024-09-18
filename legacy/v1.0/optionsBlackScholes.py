import numpy as np
import scipy.stats as stats

#easy function access
N = stats.norm.cdf

def dcalc(S, K, T, r, sigma, q=0):
    '''
    Calculates the d function of Black Scholes Model

    S: underlying price
    K: options strike price
    T: Time until expiry (years)
    r: risk free rates
    sigma: implied volatility of the options
    q: dividend of underlying

    '''
    d1 = (np.log(S/K) + (r - q + sigma**2/2)*T) /(sigma*np.sqrt(T))
    d2 = d1 -  (sigma*np.sqrt(T))
    return d1, d2


#calculate the options' price
def price(cp, S, K, T, r, sigma, q=0):
    '''
    Calculates the price of options

    cp: calls or puts
    S: underlying price
    K: options strike price
    T: Time until expiry (days)
    r: risk free rates
    sigma: implied volatility of the options
    q: dividend of underlying
    '''
    tte = T/365.0 #time in years
    d = dcalc(S, K, tte, r, sigma, q)
    d1 = d[0]
    d2 = d[1]
    if cp == "c" or cp == "call" or cp == "calls":
        return S * N(d1) - K * np.exp(-r*tte)* N(d2)
    elif cp == "p" or cp == "put" or cp == "puts":
        return K*np.exp(-r*tte)*N(-d2) - S*N(-d1)
    else:
        print("Error: not a put or call")

#calculate the delta of options
def delta(cp, S, K, T, r, sigma, q=0):
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
    tte = T/365.0 #time in years
    #calculate d1
    if T < 0.000001:
        T = 0.000001
    d = dcalc(S, K, T, r, sigma, q)
    d1 = d[0]
    d2 = d[1]
    #import gaussian cdf
    if cp == "c" or cp == "call":
        return N(d1)
    if cp == "p" or cp == "put":
        return N(d1) -1
    else:
        print("Error: not a put or call")

def impVol():
    return 1