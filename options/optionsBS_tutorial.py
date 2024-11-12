from scipy.stats import norm
import numpy as np
N = norm.cdf

def d1(S, K, T, r, sigma):
    return (np.log(S/K) + (r + sigma**2/2)*T) /\
                     (sigma*np.sqrt(T))

def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma* np.sqrt(T)

def delta_call(S, K, T, r, sigma):
    
    return N(d1(S, K, T, r, sigma))

    
def delta_put(S, K, T, r, sigma):
    return - N(-d1(S, K, T, r, sigma))

