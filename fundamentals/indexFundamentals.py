"""
For calculating fundamental parameters related to index funds.

Notation:
    CAGR: compound annual growth rate
"""
import numpy as np

def return_cagr (stock, start, end, period):
    """
    Calculates the compound annual return of a given stock.
    
    input:
        d
    output:
        d
    """

def return_cagr_simple (principle, duration, cagr = 9.8, inflation = 3.3):
    """
    Calculates the return on investment using given CAGR.
    
    input:
        principle: initial value of portfolio
        duration: number of years holding the portfolio
        cagr: the given cagr
            default s&p500 all time cagr
        inflation: devaluation of currency, works again cagr
            default US all time inflation
    output:
        results [float]: the final value of portfolio
    """
    annualrate = 1 + (0.01*(cagr-inflation))
    results = principle * annualrate**duration
    return results

def return_compound (principle, duration, savings=0, freq = 12, cagr = 9.8, inflation = 3.3):
    """
    Calculates the return on investment using given CAGR, with savings adde
    to the portfolio each year.
    
    input:
        principle: initial value of portfolio
        duration: number of years holding the portfolio
        savings: how much money is added over each period
        frequency: how many times does the saving come in and principle compound per year 
            default 12 per year, i.e. monthly
        cagr: the given cagr
            default s&p500 all time cagr
        inflation: devaluation of currency, works again cagr
            default US all time inflation
    output:
        results [float]: the final value of portfolio
    """
    period = int(duration*freq)
    rate = 1 + (0.01*(cagr-inflation)/freq)
    
    results = principle
    for i in range(0, period):
        results = results * rate + savings
        
    return results

def debt_repayment(initial, payment=0, freq = 12, interest = 9.8, inflation = 3.3, custom_max=100):
    """
    Calculates how long does it take to repay debt.
    
    input:
        initial: initial value of loan
        payment: how much money is added over each period
        frequency: how many times does the saving come in and principle compound per year 
            default 12 per year, i.e. monthly
        interest: annual interest rate
            default s&p500 all time cagr
        inflation: devaluation of currency
            default US all time inflation
        custom_max: custom maximum number of years in case the debt cannot be repayed.
            default 100 years
    output:
        results [int]: the number of years required for repayment
    
    NOTE: solved interatively.
    """
    rate = 1 + (0.01*interest/freq)
    infl = 1 + (0.01*inflation/freq)
    results = initial
    
    #check if it is possible to pay back the debt
    if (results * rate / infl) - results > payment:
        raise ValueError("Repayment not possible due to interest been higher than payment.")
        return None
    
    #iterate until custom_max
    for i in range(0, freq*custom_max):
        results = (results * rate / infl) - payment
        #print(f"month {i}: {results}")
        if results <=0:
            return i/freq
    
    raise ValueError(f"Repayment period over {custom_max} years.")
    return None

def debt_repayment_minimum(initial, years = 12, freq = 12, interest = 9.8, inflation = 3.3):
    """
    Calculates how much you need to pay to fully repay the loan in given duration
    
    input:
        initial: initial value of loan
        years: number of years to pay the loan over
        frequency: how many times does the saving come in and principle compound per year 
            default 12 per year, i.e. monthly
        interest: annual interest rate
            default s&p500 all time cagr
        inflation: devaluation of currency
            default US all time inflation
    output:
        results [int]: the number of years required for repayment
    
    NOTE: uses formula derived from geometric series
    """
    #get the base value of interest, inflation, and number of periods
    inte = 1 + (0.01*interest/freq)
    infl = 1 + (0.01*inflation/freq)
    periods = freq * years
    
    #find the total rate of change of loan value
    rate = inte / infl
    
    #calculate the minimum payment using geometric series
    results = initial * (rate - 1 )/(1 - (rate**(-periods)))
    
    return results
