import indicators as h
import numpy as np
import optionsBlackScholes as options
import pandas as pd

S = 223
K1 = 200
K2 = 190
sigma1 = 0.612
sigma2 = 0.629
#sigma1 = 0.181
#sigma2 = 0.198
r = 0.0475

T = 28

c = "call"
p = "put"

def table(cp, S, K1, K2, T, r, sigma1, sigma2, prange=20, trange=5):
    print (
        '''
        Current Price = {}
        Strike 1 = {}
        Strike 2 = {}
        Time to Expiry = {}
        IV 1 = {}
        IV 2 = {}
        '''.format(S, K1, K2, T, sigma1, sigma2))
    
    if (cp == "p") or (cp == "put"):
        prange = prange * -1
    #range variables
    S1 = int(S + ((7/4)*prange))
    S2 = int(S - ((1/4)*prange))
    T1 = int(T - trange)
    
    #create dataframe
    df = pd.DataFrame(
        {"Underlying": [i for i in range (S1, S2)]}
    )
    
    #iterate through time
    for i in reversed(range(T1, T + 1)):  
        sprd = [] #spread list
        for j in range (S1, S2):
            p1 = options.price(j, K1, i, r, sigma1, cp)
            p2 = options.price(j, K2, i, r, sigma2, cp)
            sp = p1 - p2
            sprd.append(sp)
        df[f"T-{i}"] = sprd

    return df
def spread(S, K1, K2, T, r, sigma1, sigma2):
    p1 = options.price(S, K1, T, r, sigma1, "c")
    p2 = options.price(S, K2, T, r, sigma2, "c")
    sp = p1 - p2


    print (
        '''
        Strike 1: %s
        Strike 2: %s

        Price 1: %s
        Price 2: %s

        spread price: %s


        '''%(K1, K2, p1, p2, sp))

