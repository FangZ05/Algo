#calculator for fixed incomes
import datetime as dt


def bond_return(coupon, matdate = None, expr = 1, r = 0):
    """
    calculates bond return using face value.

    input:
        coupon : coupon rate in percent.
        expr: number of days to maturity. default 1 day.
        matdate: maturity date. Using string in 'Y-M-D' format
        r: risk-free rate, typically the central bank cash rate. Default 0, i.e. true return

    output:
        results: amount of return on the bond.
    """
    #get number of days to maturity
    if matdate is not None:
        #for a maturity date is provided
        today = dt.datetime.today()
        exprdate = dt.datetime.strptime(expr, "%Y-%m-%d")
        tdelta = abs(today - exprdate).days
    else:
        #number of days to maturity is provided
        tdelta = expr

    T = tdelta/365.0 #time to maturity
    results = (1+coupon)**T
    return results

def bond_value(F, coupon, matdate = None, expr = 1, r = 0):
    """
    calculate bond return using face value.

    input:
        F: face value of bond.
        coupon : coupon rate in percent.
        expr: number of days to maturity. default 1 day.
        matdate: maturity date. Using string in 'Y-M-D' format
        r: risk-free rate, typically the central bank cash rate. Default 0, i.e. true return
    
    output:
        results: current value of the bond
    """
    #calculate return of the bond
    rate = bond_return(coupon, matdate = matdate, expr = expr, r = r)

    #calculate current value
    results = F/rate

    return results

def discount_cashflow(cfList, disRate):
    """
    Calculates the discount cashflow
    """
    return 0