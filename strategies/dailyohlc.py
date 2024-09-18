from strategies.common_strategies import *

def minute_range_15(pricedfChrono, principle, start, period = 5, verbose = False):
    """
    a backtest strategy using 15 minute range.

    15 minute range: set the first 15 minute candle of the day as entry and stoploss.
        buy price break either high or low of candle. Stoploss when price break the other way.
        Take profit defined by a ratio of the stoploss.
    
    ticker: ticker of the stock. String.
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    """
    if verbose:
        print(f"starting date: {start}")

    #get price in chronological order
    #pricedfChrono = clean.stock_data_reversetime(pricedf)
    
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

    #get a list of the opening candle w/ time = 9:30 nytz
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)

    pricedfChrono['lunch'] = pricedfChrono['Time'].dt.time == dt.time(12,0)

    #initialize some values
    resistance = 999999
    support = 0
    stoplossgap = 0
    portfolioStock = 0
    successrate = 0
    successtrades = 0
    principleprev = principle
    closedtrades = 0
    shareprice = 0
    shares = 0
    #close the position
    def close_position():
        nonlocal principle
        nonlocal cashflow
        nonlocal shares
        nonlocal portfolioStock
        nonlocal closedtrades
        nonlocal successtrades
        principle, cashflow, shares = close(principle, shareprice, portfolioStock)
        portfolioStock -= shares
        
        closedtrades +=1
        if principle > principleprev:
            successtrades +=1
        if verbose:
            print(f"Current time: {i}")
            print(f"Current price: {shareprice}")
            print(f"Current principle: {principle}")
            print(f"Total trades: {successtrades}")
            print(f"Successful trades: {successtrades}")
    #iterate over all time in the given period
    
    for i in givenTime:
        #get the location of the current time
        loc = pricedfChrono[timeChrono==i].index[0]
        iloc = pricedfChrono.index.get_loc(loc)

        #get the data of current time
        row = pricedfChrono.iloc[iloc]
        shareprice = row['Close']
        #check if this is an opening candle
        if row['bell']:
            #get the resistance and support
            resistance = row['High']
            support = row['Low']
        
        #====sudo code====#
        if portfolioStock == 0:
            #when there is no open position
            if shareprice > resistance:

                    
                #get the stoploss and target
                stoplossgap = shareprice - support
                stoploss = support
                target = (stoplossgap*2) + shareprice

                principleprev = principle
                
                if verbose:
                    print(f"Current time: {i}")
                    print(f"Current price: {shareprice}")
                    print(f"Current principle: {principle}")
                    print(f"going long")
                #if the price moved above resistance
                principle, cashflow, portfolioStock = long(principle, shareprice)


            elif shareprice < support:
    
                #get the stoploss and target
                stoplossgap = resistance - shareprice
                stoploss = resistance
                target = shareprice - (stoplossgap * 2)
                                        
                if verbose:
                    print(f"Current time: {i}")
                    print(f"Current price: {shareprice}")
                    print(f"Current principle: {principle}")
                    print(f"going short")
                principleprev = principle
                
                #if the price moved below support
                principle, cashflow, portfolioStock = short(principle, shareprice)
                


        if portfolioStock > 0:
            #when there is long positionsd
            if shareprice > target:
                #sell when reached target
                close_position()
            if shareprice < stoploss:
                #sell when reached stoploss
                close_position()
            if row['lunch']:
                #sell when time is up
                close_position()
                
        if portfolioStock < 0:
            #when there is long position
            if shareprice < target:
                #sell when reached target
                close_position()
            if shareprice > stoploss:
                #sell when reached stoploss
                close_position()
            if row['lunch']:
                #sell when time is up
                close_position()
                
    close_position()
    successrate = successtrades/closedtrades         
    return principle, successrate
def minute_range_15_modified(pricedfChrono, principle, start, period = 5, verbose = False):
    """
    a backtest strategy using 15 minute range. Sell half of the position when reached first target.

    15 minute range: set the first 15 minute candle of the day as entry and stoploss.
        buy price break either high or low of candle. Stoploss when price break the other way.
        Take profit defined by a ratio of the stoploss.
    
    ticker: ticker of the stock. String.
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    """
    if verbose:
        print(f"starting date: {start}")

    #get price in chronological order
    #pricedfChrono = clean.stock_data_reversetime(pricedf)
    
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

    #get a list of the opening candle w/ time = 9:30 nytz
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)

    pricedfChrono['lunch'] = pricedfChrono['Time'].dt.time == dt.time(12,0)

    #initialize some values
    resistance = 999999
    support = 0
    stoplossgap = 0
    portfolioStock = 0
    successrate = 0
    successtrades = 0
    principleprev = principle
    closedtrades = 0
    shareprice = 0
    shares = 0
    #close the position
    def close_position():
        nonlocal principle
        nonlocal cashflow
        nonlocal shares
        nonlocal portfolioStock
        nonlocal closedtrades
        nonlocal successtrades
        principle, cashflow, shares = close(principle, shareprice, portfolioStock)
        portfolioStock -= shares
        
        closedtrades +=1
        if principle > principleprev:
            successtrades +=1
        if verbose:
            print(f"Current time: {i}")
            print(f"Current price: {shareprice}")
            print(f"Current principle: {principle}")
            print(f"Total trades: {successtrades}")
            print(f"Successful trades: {successtrades}")
    #iterate over all time in the given period
    
    for i in givenTime:
        #get the location of the current time
        loc = pricedfChrono[timeChrono==i].index[0]
        iloc = pricedfChrono.index.get_loc(loc)

        #get the data of current time
        row = pricedfChrono.iloc[iloc]
        shareprice = row['Close']
        #check if this is an opening candle
        if row['bell']:
            #get the resistance and support
            resistance = row['High']
            support = row['Low']
        
        #====sudo code====#
        if portfolioStock == 0:
            #when there is no open position
            if shareprice > resistance:

                    
                #get the stoploss and target
                stoplossgap = shareprice - support
                stoploss = support
                target1 = stoplossgap + shareprice
                target2 = (stoplossgap * 2) + shareprice
                principleprev = principle
                
                if verbose:
                    print(f"Current time: {i}")
                    print(f"Current price: {shareprice}")
                    print(f"Current principle: {principle}")
                    print(f"going long")
                #if the price moved above resistance
                principle, cashflow, portfolioStock = long(principle, shareprice)


            elif shareprice < support:
    
                #get the stoploss and target
                stoplossgap = resistance - shareprice
                stoploss = resistance
                target1 = shareprice - stoplossgap
                target2 = shareprice - (stoplossgap * 2)
                                        
                if verbose:
                    print(f"Current time: {i}")
                    print(f"Current price: {shareprice}")
                    print(f"Current principle: {principle}")
                    print(f"going short")
                principleprev = principle
                
                #if the price moved below support
                principle, cashflow, portfolioStock = short(principle, shareprice)
                


        if portfolioStock > 0:
            #when there is long positionsd
            if shareprice > target1:
                #sell half when reached target
                principle, cashflow, shares = close(principle, shareprice, portfolioStock/2)
                portfolioStock -= shares

                stoploss = shareprice - (stoplossgap)

            if shareprice > target2:
                #sell when reached target
                close_position()
            if shareprice < stoploss:
                #sell when reached stoploss
                close_position()
            if row['lunch']:
                #sell when time is up
                close_position()
                
        if portfolioStock < 0:
            #when there is long position
            if shareprice < target1:
                #sell half when reached target
                principle, cashflow, shares = close(principle, shareprice, portfolioStock/2)
                portfolioStock -= shares

                stoploss = shareprice + (stoplossgap)
            if shareprice < target2:
                #sell when reached target
                close_position()
            if shareprice > stoploss:
                #sell when reached stoploss
                close_position()
            if row['lunch']:
                #sell when time is up
                close_position()
                
    close_position()
    successrate = successtrades/closedtrades         
    return principle, successrate

def minute_range_15_modified_sma(pricedfChrono, principle, start, period = 5, verbose = False):
    """
    a backtest strategy using 15 minute range.

    15 minute range: set the first 15 minute candle of the day as entry and stoploss.
        buy price break either high or low of candle. Stoploss when price break the other way.
        Take profit defined by a ratio of the stoploss.
    
    ticker: ticker of the stock. String.
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    """
    if verbose:
        print(f"starting date: {start}")

    #get price in chronological order
    #pricedfChrono = clean.stock_data_reversetime(pricedf)
    
    #get the 200 sma
    pricedfChrono['sma'] = pricedfChrono.ta.sma(200).fillna(pricedfChrono['Close'])

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

    #get a list of the opening candle w/ time = 9:30 nytz
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)

    pricedfChrono['lunch'] = pricedfChrono['Time'].dt.time == dt.time(12,0)

    #initialize some values
    resistance = 999999
    support = 0
    stoplossgap = 0
    portfolioStock = 0
    successrate = 0
    successtrades = 0
    principleprev = principle
    closedtrades = 0
    shareprice = 0
    shares = 0
    #close the position
    def close_position():
        nonlocal principle
        nonlocal cashflow
        nonlocal shares
        nonlocal portfolioStock
        nonlocal closedtrades
        nonlocal successtrades
        principle, cashflow, shares = close(principle, shareprice, portfolioStock)
        portfolioStock -= shares
        
        closedtrades +=1
        if principle > principleprev:
            successtrades +=1
        if verbose:
            print(f"Current time: {i}")
            print(f"Current price: {shareprice}")
            print(f"Current principle: {principle}")
            print(f"Total trades: {successtrades}")
            print(f"Successful trades: {successtrades}")
    #iterate over all time in the given period
    
    for i in givenTime:
        #get the location of the current time
        loc = pricedfChrono[timeChrono==i].index[0]
        iloc = pricedfChrono.index.get_loc(loc)

        #get the data of current time
        row = pricedfChrono.iloc[iloc]
        shareprice = row['Close']
        movingaverage = row['sma']
        #check if this is an opening candle
        if row['bell']:
            #get the resistance and support
            resistance = row['High']
            support = row['Low']
        
        #====sudo code====#
        if portfolioStock == 0:
            #when there is no open position
            if shareprice > resistance:
                if shareprice >= movingaverage:
                    #get the stoploss and target
                    stoplossgap = shareprice - support
                    stoploss = support
                    target1 = stoplossgap + shareprice
                    target2 = (stoplossgap * 2) + shareprice
                    principleprev = principle
                    
                    if verbose:
                        print(f"Current time: {i}")
                        print(f"Current price: {shareprice}")
                        print(f"Current principle: {principle}")
                        print(f"going long")
                    #if the price moved above resistance
                    principle, cashflow, portfolioStock = long(principle, shareprice)
            elif shareprice < support:
                if shareprice < movingaverage:
                    #get the stoploss and target
                    stoplossgap = resistance - shareprice
                    stoploss = resistance
                    target1 = shareprice - stoplossgap
                    target2 = shareprice - (stoplossgap * 2)
                                            
                    if verbose:
                        print(f"Current time: {i}")
                        print(f"Current price: {shareprice}")
                        print(f"Current principle: {principle}")
                        print(f"going short")
                    principleprev = principle
                    
                    #if the price moved below support
                    principle, cashflow, portfolioStock = short(principle, shareprice)
                    


        if portfolioStock > 0:
            #when there is long positionsd
            if shareprice > target1:
                #sell half when reached target
                principle, cashflow, shares = close(principle, shareprice, portfolioStock/2)
                portfolioStock -= shares

                stoploss = shareprice - (stoplossgap)

            if shareprice > target2:
                #sell when reached target
                close_position()
            if shareprice < stoploss:
                #sell when reached stoploss
                close_position()
            if row['lunch']:
                #sell when time is up
                close_position()
                
        if portfolioStock < 0:
            #when there is long position
            if shareprice < target1:
                #sell half when reached target
                principle, cashflow, shares = close(principle, shareprice, portfolioStock/2)
                portfolioStock -= shares

                stoploss = shareprice + (stoplossgap)
            if shareprice < target2:
                #sell when reached target
                close_position()
            if shareprice > stoploss:
                #sell when reached stoploss
                close_position()
            if row['lunch']:
                #sell when time is up
                close_position()
                
    close_position()
    successrate = successtrades/closedtrades 
    return principle, successrate        
    
def gap_close_buyAtOpen(pricedfChrono, principle, start, period = 5, verbose = False):
    """
    a backtest strategy using gap close by buying at open.

    pricedfChrono: price data of the stock.
    principle: initial starting money
    start: start date
    period: number of days after start days that is backtested
    """

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

    #get a list of the opening candle w/ time = 9:30 nytz, in truth table
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)

    pricedfChrono['lunch'] = pricedfChrono['Time'].dt.time == dt.time(12,0)

    pricedfChrono['dayend'] = pricedfChrono['Time'].dt.time == dt.time(15,45)

    #initialize some values
    prevClose = 0
    resistance = 999999
    support = 0
    stoplossgap = 0
    portfolioStock = 0
    successrate = 0
    successtrades = 0
    principleprev = principle
    closedtrades = 0
    shareprice = 0
    openPrice = 0
    shares = 0
    notinitiated = True
    #close the position
    def close_position():
        nonlocal principle
        nonlocal cashflow
        nonlocal shares
        nonlocal portfolioStock
        nonlocal closedtrades
        nonlocal successtrades
        principle, cashflow, shares = close(principle, shareprice, portfolioStock)
        portfolioStock -= shares
        
        closedtrades +=1
        if principle > principleprev:
            successtrades +=1
        if verbose:
            print(f"Current time: {i}")
            print(f"Current price: {shareprice}")
            print(f"Current principle: {principle}")
            print(f"Total trades: {successtrades}")
            print(f"Successful trades: {successtrades}")
    #iterate over all time in the given period
    for i in givenTime:
        #get the location of the current time
        loc = pricedfChrono[timeChrono==i].index[0]
        iloc = pricedfChrono.index.get_loc(loc)

        #get the data of current time
        row = pricedfChrono.iloc[iloc]

        #initiate to find a previous close
        if notinitiated:
            if row['dayend']:
                prevClose = row['Close']
                notinitiated = False
        else:
            #get the closing share price
            shareprice = row['Close']

            #update previous close if needed
            if row['dayend']:
                prevClose = row['Close']

            #check if this is an opening candle
            if row['bell']:
                #get the opening price
                openPrice = row['Open']
                target1 = prevClose

                #get the stoploss and target
                if openPrice > prevClose:
                    #for gapping up overnight
                    stoplossgap = openPrice - target1
                    stoploss = openPrice + stoplossgap
                    target2 = openPrice - (stoplossgap * 2)
                else:
                    #for gapping down overnight
                    stoplossgap = target1 - openPrice
                    stoploss = openPrice - stoplossgap
                    target2 = openPrice + (stoplossgap * 2)

                if portfolioStock == 0:  
                    #when there is no open position
                    principleprev = principle

                    if openPrice > prevClose:
                        #sell at open
                        principle, cashflow, portfolioStock = short(principle, openPrice)
                        if verbose:
                            print(f"Current time: {i}")
                            print(f"Current price: {shareprice}")
                            print(f"Current principle: {principle}")
                            print(f"going long")
                    else:
                        #buy at open
                        principle, cashflow, portfolioStock = long(principle, openPrice)
                        if verbose:
                            print(f"Current time: {i}")
                            print(f"Current price: {shareprice}")
                            print(f"Current principle: {principle}")
                            print(f"going long")
                    


            if portfolioStock > 0:
                #when there is long positionsd
                if shareprice > target1:
                    #sell half when reached target
                    principle, cashflow, shares = close(principle, shareprice, portfolioStock/2)
                    portfolioStock -= shares

                    stoploss = shareprice - stoplossgap

                if shareprice > target2:
                    #sell when reached target
                    close_position()
                if shareprice < stoploss:
                    #sell when reached stoploss
                    close_position()
                if row['lunch']:
                    #sell when time is up
                    close_position()
                    
            if portfolioStock < 0:
                #when there is long position
                if shareprice < target1:
                    #sell half when reached target
                    principle, cashflow, shares = close(principle, shareprice, portfolioStock/2)
                    portfolioStock -= shares

                    stoploss = shareprice + stoplossgap
                if shareprice < target2:
                    #sell when reached target
                    close_position()
                if shareprice > stoploss:
                    #sell when reached stoploss
                    close_position()
                if row['lunch']:
                    #sell when time is up
                    close_position()
                
    close_position()
    successrate = successtrades/closedtrades         
    return principle, successrate