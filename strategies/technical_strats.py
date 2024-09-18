
from strategies.common_strategies import *


#=====strategies=====#
def macd_backtest(pricedf, principle, start, period=30, verbose = False):
    """
    a backtest strategy using MACD
    
    pricedfChrono: price data of the stock in chronological order
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    """
    
    #get price in chronological order
    pricedfChrono = clean.stock_data_reversetime(pricedf)

    #find the end date
    end = start + dt.timedelta(days=period)
    
    
    priceChrono = pricedfChrono['Close'] #get the closing price for non-candlestick purpose
    timeChrono = pricedfChrono['Time']
    
    #set the start time to one of the data point
    for i in timeChrono:
        if i > start:
            start = i
            break
    
    #limit the range of the data
    givendf = pricedfChrono[((pricedfChrono['Time'] > start ) & (pricedfChrono['Time'] < end))]

    #remove timezone information of data
    givenTime = pd.to_datetime(givendf['Time'], utc=True).dt.tz_convert(nytz).dt.tz_localize(None)
    timeChrono = pd.to_datetime(timeChrono, utc=True).dt.tz_convert(nytz).dt.tz_localize(None)

    bars = 5
    period = 26
    portfolioStock = 0
    buyprice = 0
    buytrade = 0
    selltrade = 0
    successtrade = 0
    freeze = False
    principleprev = principle
    def long():
        nonlocal principle
        nonlocal portfolioStock
        nonlocal buytrade
        nonlocal buyprice
        if principle > shareprice:
            principle, cashflow, shares = buy(principle, shareprice)
            portfolioStock = portfolioStock + shares
            if shares > 0:
                buytrade += 1
                buyprice = shareprice
            if verbose: 
                print(f"Current iteration: {i}")
                print(f"Current trend: {trend}")
                print(f"Current time: {row['Time']}")
                print(f"Current roc: {roc}")
                print(f"Current lag momentum: {momentum}")
                print(f"buying stock at price = {shareprice}")
                print(f"Current principle = {principle}")
                print(f"number of buy trades = {buytrade}")
    def short():
        nonlocal principle
        nonlocal portfolioStock
        nonlocal selltrade
        nonlocal principleprev
        nonlocal successtrade
        if portfolioStock > 0:
            principle, cashflow, shares = sell(principle, shareprice, portfolioStock)
            if portfolioStock > 0:
                if principle > principleprev:
                    successtrade += 1
                principleprev = principle
                selltrade += 1
                
            portfolioStock = 0
            if verbose: 
                print(f"Current iteration: {i}")
                print(f"Current trend: {trend}")
                print(f"Current time: {row['Time']}")
                print(f"Current roc: {roc}")
                print(f"Current lag momentum: {momentum}")
                print(f"selling stock at price = {shareprice}")
                print(f"Current principle = {principle}")
                print(f"number of sell trades = {selltrade}")
    
    for i in givenTime:
        loc = pricedfChrono[timeChrono==i].index[0]
        iloc = pricedfChrono.index.get_loc(loc)
        row = pricedfChrono.iloc[iloc]
        shareprice = row['Close']
        trend = []
        for j in range(1, 1+bars):
            if iloc - j < period:    
                ilocstart = 0
            else:
                ilocstart = iloc - period - j
            trendline = an.trendbasic(priceChrono[ilocstart:iloc-j], period)
            trend.append(trendline)

        trend = np.array(trend)[::-1]
        accel = np.gradient(trend)

        roc = trend[-1]
        momentum = accel[-2]
        
        if portfolioStock > 0:
            if shareprice < (buyprice * 0.99):
                #stoploss
                short()
                freeze = False
            if shareprice > (buyprice * 1.02):
                #take profit
                short()
                freeze = False

        if ((roc > 0) & (momentum > 0)):
            if not freeze:
                if portfolioStock ==0:
                    long()
                    freeze = True
        #if momentum < 0:
            #short()
            #freeze = False

    
    #close all positions
    short()
    successrate = successtrade/selltrade
    print(f"test: r={successtrade}, s={selltrade}")
    return principle, successrate


