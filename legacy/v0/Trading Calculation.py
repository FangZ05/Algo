import math
import matplotlib

def ptl(): #profit loss ratio of a stock
    stock = input("Entre the ticker symbol: ")
    p = input("Entre the current stock price: ")
    s = input("Entre the support price(optional): ")
    r = input("Entre the resistance price(optional): ")
    try:
        float(p)
    except Exception:
        print ("Please entre ticker and stock price properly!")
        return
    else:
        if stock == "":
            print ("Please entre ticker and stock price properly!")
        else:
            p = float(p)
    try:
        float(s)
    except Exception:
        pass
    else:
        s = float (s)
    try:
        float(r)
    except Exception:
        pass
    else:
        r = float(r)
    print ("ticker: %a,"%stock, "trading at: %a"%p, \
           ", support at: %s"%s if type(s)==float else "", \
           ", resustance at %r"%r if type(r)==float else "")
    if type(s)!=float:
        if type(r)!=float:
            print("the program can't do much without both support and resistance.")
        else:
            gainPercent = ((r/p)-1)*100
            print ("Profit potential: %a" %gainPercent)
    else:
        if s >= p:
            print ("Support must be lower than prcie!")
            return
        if type(r)!=float:
            lossPercent = (1- (s/p))*100
            rLossPercent = ((p/s)-1)*100
            print ("Loss potential %a" %lossPercent)
            print ("Real loss potential: %a" %rLossPercent)
        else:
            if p >= r:
                print ("Price must be lower than resistance!")
                return
            else:
                lossPercent = (1- (s/p))*100
                gainPercent = ((r/p)-1)*100
                PTL = gainPercent/lossPercent
                rLossPercent = ((p/s)-1)*100
                RPTL = gainPercent/rLossPercent
                print ("Profit potential: %a" %gainPercent)
                print ("Loss potential: %a" %lossPercent)
                print ("Real profit poential: %a" %gainPercent)
                print ("Real percent loss: %a" %rLossPercent)
                print ("Profit to Loss ratio: %a" %PTL)
                print ("Real Profit to Loss Ratio: %a" %RPTL)
                if RPTL <= 2:
                    print ("Risk too high, do not entre position")

def option():
    return 1;
    
def FibbRetrscement(stock: tuple):
    p = stock[0]
    s = stock[1]
    r = stock[2]
    print ("1.000 level: %a" %r)
    print ("0.886 level: %a" %((r-s)*0.886+s))
    print ("0.786 level: %a" %((r-s)*0.786+s))
    print ("0.618 level: %a" %((r-s)*0.618+s))
    print ("0.500 level: %a" %((r-s)*0.500+s))
    print ("0.382 level: %a" %((r-s)*0.382+s))
    print ("0.236 level: %a" %((r-s)*0.236+s))
    print ("0.000 level: %a" %s)

def qPTL(p: float, s: float, r: float): #manual calculation of PTL
    print ("price: %a"%p)
    print ("support: %a" %s)
    print ("resistance: %a" %r)
    lossPercent = (1- (s/p))*100
    gainPercent = ((r/p)-1)*100
    PTL = gainPercent/lossPercent
    rLossPercent = ((p/s)-1)*100
    RPTL = gainPercent/rLossPercent
    print ("percent gain: %a" %gainPercent)
    print ("percent loss: %a" %lossPercent)
    print ("real percent gain: %a" %gainPercent)
    print ("real percent loss: %a" %rLossPercent)
    print ("Profit to Loss ratio: %a" %PTL)
    print ("Real Profit to Loss Ratio: %a" %RPTL)
    
