"""
Technical analysis using options.
"""

import numpy as np
from options.optionsBlackScholes import options
import talib
import pandas_ta

calls = ['C', 'CALL', 'CALLS']
puts = ['P', 'PUT', 'PUTS']
MAD = np.sqrt(2/np.pi) #mean absolute deviation

def GEX(options):
    """
    Calculates the GEX exposure of an option chain.

    Input:
        options: the option chain
    """

    GEX_raw = options['open_interest'].astype(float) * options['Gamma'].astype(float) * 100
    right = options['right'].apply(str.upper).isin(calls)

    options['GEX'] = np.where(right, GEX_raw, -GEX_raw)
    return options

def GEX_keylevel(options):
    """
    Identify levels with maximum and minimum GEX
    """
    GEX = options['GEX']
    call_level = options.loc[GEX.idxmax(), 'strike']
    put_level = options.loc[GEX.idxmin(), 'strike']

    print(f"call_level: {call_level}, put_level: {put_level}")
    return call_level, put_level

def expected_move(price, options, verbose = False):

    
    #get the important columns
    strike = options['strike']
    right = options['right'].apply(str.upper)

    
    #find the two closest strike
    strike_ceil = strike[strike > price].min()
    strike_floor = strike[strike < price].max()

    #get the weighting of two strikes, i.e. closer to the strike higher the weight
    gap = strike_ceil - strike_floor
    weight_ceil = 1- ((strike_ceil - price)/gap)
    weight_floor = 1 -((price - strike_floor)/gap)

    """
    #get the bid & ask for the 4 options at these strikes and calculate the mid
    call_ceil_bid = options.loc[(strike == strike_ceil) & (right.isin(calls)), 'BID'].iloc[0]
    call_ceil_ask = options.loc[(strike == strike_ceil) & (right.isin(calls)), 'ASK'].iloc[0]
    put_ceil_bid = options.loc[(strike == strike_ceil) & (right.isin(puts)), 'BID'].iloc[0]
    put_ceil_ask = options.loc[(strike == strike_ceil) & (right.isin(puts)), 'ASK'].iloc[0]
    call_floor_bid = options.loc[(strike == strike_floor) & (right.isin(calls)), 'BID'].iloc[0]
    call_floor_ask = options.loc[(strike == strike_floor) & (right.isin(calls)), 'ASK'].iloc[0]
    put_floor_bid = options.loc[(strike == strike_floor) & (right.isin(puts)), 'BID'].iloc[0]
    put_floor_ask = options.loc[(strike == strike_floor) & (right.isin(puts)), 'ASK'].iloc[0]

    call_ceil_mid = (call_ceil_bid + call_ceil_ask)/2
    put_ceil_mid = (put_ceil_bid + put_ceil_ask)/2
    call_floor_mid = (call_floor_bid + call_floor_ask)/2
    put_floor_mid = (put_floor_bid + put_floor_ask)/2
    """
    try:
        call_ceil_mid = (options.loc[(strike == strike_ceil) & (right.isin(calls)), 'MID'].iloc[0])
        put_ceil_mid = (options.loc[(strike == strike_ceil) & (right.isin(puts)), 'MID'].iloc[0])
        call_floor_mid = (options.loc[(strike == strike_floor) & (right.isin(calls)), 'MID'].iloc[0])
        put_floor_mid = (options.loc[(strike == strike_floor) & (right.isin(puts)), 'MID'].iloc[0])

        #calculate the expected move
        call_leg = (call_ceil_mid * weight_ceil) + (call_floor_mid * weight_floor)
        put_leg = (put_ceil_mid * weight_ceil) + (put_floor_mid * weight_floor)

    except:
        #if there is an error finding the market price of each option
        print("Error finding market price, returning zeroes.")
        call_leg = 0
        put_leg = 0


    exp_move = (1/MAD)*(call_leg + put_leg )/2
    exp_move_up = (1/MAD)*call_leg
    exp_move_down = (1/MAD)*put_leg
    exp_move_percent = 100*exp_move/price

    #debugs
    if verbose:
        print(f"ceil strike: {strike_ceil}, floor strike: {strike_floor}")
        print(f"weight ceil: {weight_ceil}, weight floor: {weight_floor}")
        print(f"ceil call MID: {call_ceil_mid}, ceil put MID: {put_ceil_mid}")
        print(f"floor call MID: {call_floor_mid}, floor put MID: {put_floor_mid}")
        print(f"straddle call: {call_leg}, straddle put: {put_leg}")

    print(f"Current price: {price}, Expected move: {exp_move:.2f}, {exp_move_percent:.4f}%")
    print(f"Expected range: {(price + exp_move_up):.2f} -> {(price - exp_move_down):.2f}")
    return exp_move, exp_move_percent, exp_move_up, exp_move_down