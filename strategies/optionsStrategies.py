if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)
    
import numpy as np
from options.optionsBlackScholes import options
import pandas as pd
from copy import deepcopy


def theta_optimal_t(options, verbose = False):
    """
    Brute force finds the optimal theta of an option based on time.
    
    input:
        options: an options object.
        verbose: for detailed output at each step
    """
    #duplicate the option for use
    curr = deepcopy(options)
    
    #define the time domain
    domain = np.arange (0, int(max(options.tte*2, 14)), 1)
    
    #iterate for all time within the domain
    bestT = 0
    bestTheta = 9999
    for i in domain:
        #change the tte of option to different times
        curr.tte = i
        theta = curr.theta
        
        #check if the current theta is better
        if theta < bestTheta:
            bestTheta = theta
            bestT = i
        
        #if we want to see all thetas
        if verbose:
            print(f"Current tte: {i}, the greeks are: {curr.greeks}")

    print(f"Best theta at: {bestT} til expiry")
    print(f"Best theta is: {bestTheta}")
    return bestT, bestTheta

def theta_optimal_K(options, verbose = False):
    """
    Brute force finds the optimal risk vs. reward strike if we are interested
    in letting the option expire worthless
    
    input:
        options: an options object.
        verbose: for detailed output at each step
        
    NOTE:
        the delta of an option is used as its chance to expire ITM
    """
    #duplicate the option for use
    curr = deepcopy(options)

    #define the strike domain
    if curr.K < 11:
        raise ValueError("This algo does not work with penny stocks.")
        return None
    else:
        strikes = max(int(curr.K * 0.1), 10)
        domain = np.arange (curr.K - strikes, curr.K + strikes, 1)
    
    #iterate for all time within the domain
    bestK = 0
    bestTheta = 9999
    bestpayout = 9999
    for i in domain:
        #change the tte of option to different times
        curr.K = i
        
        #get the required parameters
        theta = curr.theta
        p = curr.delta
        
        #estimate the payout
        payout = theta*(1-p)
        
        #check if the current theta is better
        if payout < bestpayout:
            bestTheta = theta
            bestK = i
            bestpayout = payout
        
        #if we want to see all thetas
        if verbose:
            print(f"Current strike: {i}, the greeks are: {curr.greeks}")
            print(f"current expected daily payout: {payout}")

    print(f"Best theta at strike: {bestK}")
    print(f"Best theta is: {bestTheta}")
    return bestK, bestTheta

def theta_optimal_roll(option1, option2, verbose=False):
    """
    Brute force finds the optimal time where it would be better to
    roll over options from one strike to another
    
    input:
        options1: currently held option
        options2: planned to held option
        *roll_period: number of days to roll the option out by
        verbose: for detailed output at each step
    """
    
    return 0

def theta_optimal_diagonal(diag1, diag2, verbose=False):
    """
    Brute force finds the optimal risk vs. reward strike assuming we
    are buying a diagonal spread
    
    logic: 
    
    input:
        options: an options object.
        verbose: for detailed output at each step
        
    NOTE:
        the delta of an option is used as its chance to expire ITM
    """



    return 0


if __name__ == '__main__':
    c = 'c'
    p = 'p'
    
    def optimize(options):
        results = deepcopy(options)
        for i in range(10):
            results.tte = theta_optimal_t(results)[0]
            results.K = theta_optimal_K(results)[0]
            
        









"""
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
"""
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

