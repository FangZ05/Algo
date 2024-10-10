#calculator for bonds
import datetime as dt

def TBond(S, expr, rate = 0):
    today = dt.datetime.today()
    exprdate = dt.datetime.strptime(expr, "%Y-%m-%d")
    tdelta = abs(today - exprdate).days
    rate = ((100.0/S)-1 + rate)*(365.0/tdelta) 
    return rate
