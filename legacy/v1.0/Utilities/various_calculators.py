# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 23:28:54 2024

@author: Fang
"""
import math as m

def leveraged_etf_est(price, move, leverage):
    #estimates moves in leveraged etf
    exp_move = leverage*move/100
    result = price * (1+ exp_move)
    print(f"Calculating {leverage}X leveraged ETF price. \n",
          f"Current etf price: {price}\n",
          f"Expected move: {exp_move*100}%\n",
          f"Expected price: {result}\n"
          )
    return (result, exp_move)

def kelly_criterion (p, q, t, s):
    """
    Calculates the Kelly Criterion, the optimal risk.
    
    P: probability of win
    q: probability of loss
    s: percent loss per loss
    t: percent gain per gain
    """
    return (p/s) - (q/t)

def kelly_winrate(r, t, s):
    """
    Calculates the expected win rate using Kelly Criterion
    
    r: risk, default 1
    s: percent loss per loss
    t: percent gain per gain
    """
    return ((s*t*r)+s)/(t+s)

def expected_return_median (p, q, t, s, n, r = 1):
    """
    Calculates the expected median return.
    
    P: probability of win
    q: probability of loss
    t: percent gain per move
    s: percent loss per move
    
    n: number of tries
    r: bet as a percentage of total principle
    """
    e_win =  (1 + (r*t))**(n*p)#expected wins
    e_loss = (1 - (r*s))**(n*q) #expected loss
    return e_win*e_loss

def probability_sigmoid (a, k, t):
    """
    model the probability using sigmoid function
    
    a: quality of probability
        how good the strategy actually is
    k: scalability of probability
        how does the probability change with higher expected move
    t: percent gain per move
    """
    return 1 / (1 + (a*m.exp(k*t)))

#base calculation
#t = 0.2
#s = t/2
#p = probability_sigmoid (0.25, 4.5, t)
#q = 1 - p
def est_kelly (price, moveU, moveD, leverage):
    #estimate several kelly criterion related parameters for a leveraged etf
    t = leveraged_etf_est(price, moveU, leverage)[1]
    s = leveraged_etf_est(price, -1*moveD, leverage)[1] * -1
    p = kelly_winrate(1, t, s)
    q = 1 - p
    print(f"Expected Winrate for break even is {p*100}%")
