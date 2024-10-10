
import datetime as dt

def gap_close(pricedfChrono):
    """
    Analyse the number of times that stocks closes the gap

    pricedfChrono: daily price data of the stock in chronological order
    """
    #initiate variables
    closedGap = 0
    prevClose = 0
    truthTable = [True]
    #Look through all available data, from second date on
    for i, rows in pricedfChrono.iterrows():
        if i == 0:
            #initiate for the first date
            prevClose = rows['Close']
        else:
            #see if the price on the day reached the previous close
            currHigh = rows['High']
            currLow = rows['Low']
            if (currHigh > prevClose) & (currLow < prevClose):
                closedGap += 1
                truthTable.append(True)
            else:
                truthTable.append(False)
            prevClose = rows['Close']

    #calculate the precent of time this worked
    successrate = closedGap/pricedfChrono.shape[0]

    #assign the truthtable to dataframe
    pricedfChrono['Gap Close'] = truthTable
    return successrate, pricedfChrono


def gap_close_intraday(pricedfChrono, interval, verbose = False):
    """
    Analyse the number of times that stocks closes the gap. For intraday data.

    pricedfChrono: price data of the stock in chronological order
    """
    #initiate variables
    closedGap = 0
    prevClose = 0
    currOpen = 0
    totaldays = 0
    notinitiated = True

    #get a list of key times
    minutes = 60 - interval
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)

    pricedfChrono['dayend'] = pricedfChrono['Time'].dt.time == dt.time(15,minutes)

    #Look through all available data, from second date on
    for i, row in pricedfChrono.iterrows():
        time = row['Time']
        if verbose:
                print(f'Current time is: {time}')
        #find the current open
        if row['bell']:
            currOpen = row['Open']
            totaldays += 1
            if verbose:
                print(f'Currently at opening bell, update current open')
        if notinitiated:
            #check if we already reached previous open
            if verbose:
                print(f'not initiated = {notinitiated}, pass')
            pass

        else:
            #get the current price range
            currHigh = row['High']
            currLow = row['Low']
            if verbose:
                print(f'Previous Close is: {prevClose}')
                print(f'Current Open is: {currOpen}')
                print(f'Current High is: {currHigh}')
                print(f'Current Low is: {currLow}')
            #see if the price on the day reached the previous close
            if currOpen > prevClose:
                #for gap up overnight
                if verbose:
                    print(f'Current open > previous Close')
                if (currLow < prevClose):
                    closedGap += 1
                    notinitiated = True

            else:
                #for gap down overnight
                if verbose:
                    print(f'Current open < previous Close')
                if (currHigh > prevClose):
                    closedGap += 1
                    notinitiated = True

        #update the previous close
        if row['dayend']:
            prevClose = row['Close']
            notinitiated = False
            if verbose:
                print(f'Currently at Closing bell, update previous close')
                print(f'notinitiated = {notinitiated}')
    #calculate the precent of time this worked
    successrate = closedGap/totaldays

    return closedGap, totaldays, successrate

def gap_close_intraday_beforelunch(pricedfChrono, interval, verbose = False):
    """
    Analyse the number of times that stocks closes the gap. For intraday data.

    pricedfChrono: price data of the stock in chronological order
    interval: interval in minutes
    """
    #initiate variables
    closedGap = 0
    prevClose = 0
    currOpen = 0
    totaldays = 0
    notinitiated = True

    #get a list of key times
    minutes = 60 - interval
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)
    pricedfChrono['lunch'] = pricedfChrono['Time'].dt.time == dt.time(12,0)
    pricedfChrono['dayend'] = pricedfChrono['Time'].dt.time == dt.time(15,minutes)

    #Look through all available data, from second date on
    for i, row in pricedfChrono.iterrows():
        time = row['Time']
        if verbose:
                print(f'Current time is: {time}')
        #find the current open
        if row['bell']:
            currOpen = row['Open']
            totaldays += 1
            if verbose:
                print(f'Currently at opening bell, update current open')
        if row['lunch']:
            #skip the day if it is pass lunch time
            notinitiated = True

        if notinitiated:
            #check if we already reached previous open
            if verbose:
                print(f'not initiated = {notinitiated}, pass')
            pass

        else:
            #get the current price range
            currHigh = row['High']
            currLow = row['Low']
            if verbose:
                print(f'Previous Close is: {prevClose}')
                print(f'Current Open is: {currOpen}')
                print(f'Current High is: {currHigh}')
                print(f'Current Low is: {currLow}')
            #see if the price on the day reached the previous close
            if currOpen > prevClose:
                #for gap up overnight
                if verbose:
                    print(f'Current open > previous Close')
                if (currLow < prevClose):
                    closedGap += 1
                    notinitiated = True

            else:
                #for gap down overnight
                if verbose:
                    print(f'Current open < previous Close')
                if (currHigh > prevClose):
                    closedGap += 1
                    notinitiated = True

        #update the previous close
        if row['dayend']:
            prevClose = row['Close']
            notinitiated = False
            if verbose:
                print(f'Currently at Closing bell, update previous close')
                print(f'notinitiated = {notinitiated}')
    #calculate the precent of time this worked
    successrate = closedGap/totaldays

    return closedGap, totaldays, successrate

def gap_close_strict(pricedfChrono):
    """
    Analyse the number of times that stocks closes the gap, more strict criterion

    pricedfChrono: price data of the stock in chronological order
    """
    #initiate variables
    closedGap = 0
    prevClose = 0
    truthTable = [True]
    #Look through all available data, from second date on
    for i, rows in pricedfChrono.iterrows():
        if i == 0:
            #initiate for the first date
            prevClose = rows['Close']
        else:
            #see if the price on the day reached the previous close
            currHigh = rows['High']
            currLow = rows['Low']
            currOpen = rows['Open']
            if (currOpen > prevClose):
                if currLow < prevClose:
                    closedGap += 1
            else:
                if currHigh > prevClose:
                    closedGap += 1 
            prevClose = rows['Close']

    #calculate the precent of time this worked
    successrate = closedGap/pricedfChrono.shape[0]
    return successrate

def gap_close_intraday_beforelunch_risk(pricedfChrono, interval, verbose = False):
    """
    Analyse the risk of not closing the gap before lunch

    pricedfChrono: price data of the stock in chronological order
    interval: interval in minutes
    """
    #initiate variables
    closedGap = 0
    prevClose = 0
    currOpen = 0
    totaldays = 0
    notinitiated = True
    risk = 0
    risklist = []
    maxrisk = 0

    #get a list of key times
    minutes = 60 - interval
    pricedfChrono['bell'] = pricedfChrono['Time'].dt.time == dt.time(9,30)
    pricedfChrono['lunch'] = pricedfChrono['Time'].dt.time == dt.time(12,0)
    pricedfChrono['dayend'] = pricedfChrono['Time'].dt.time == dt.time(15,minutes)

    #Look through all available data, from second date on
    for i, row in pricedfChrono.iterrows():
        #get the current data
        time = row['Time']
        currHigh = row['High']
        currLow = row['Low']
        if verbose:
                print(f'Current time is: {time}')

        #find the current open
        if row['bell']:
            currOpen = row['Open']
            totaldays += 1
            if verbose:
                print(f'Currently at opening bell, update current open')

        if row['lunch']:
            #skip the day if it is pass lunch time
            notinitiated = True
        
        if notinitiated:
            #check if we already reached previous open
            if verbose:
                print(f'not initiated = {notinitiated}, pass')

        else:
            #see if the price on the day reached the previous close
            if verbose:
                print(f'Previous Close is: {prevClose}')
                print(f'Current Open is: {currOpen}')
                print(f'Current High is: {currHigh}')
                print(f'Current Low is: {currLow}')
            
            if currOpen > prevClose:
                #for gap up overnight
                if verbose:
                    print(f'Current open > previous Close')
                
                #calculate risk
                risk = currHigh - currOpen
                if risk > maxrisk:
                    maxrisk = risk

                if (currLow < prevClose):
                    closedGap += 1
                    notinitiated = True

            else:
                #for gap down overnight
                if verbose:
                    print(f'Current open < previous Close')
                #calculate risk
                risk = currOpen - currLow
                if risk > maxrisk:
                    maxrisk = risk

                if (currHigh > prevClose):
                    closedGap += 1
                    notinitiated = True

        #update the previous close
        if row['dayend']:
            prevClose = row['Close']
            notinitiated = False
            risklist.append(100*maxrisk/prevClose)
            maxrisk = 0
            if verbose:
                print(f'Currently at Closing bell, update previous close')
                print(f'notinitiated = {notinitiated}')
    #calculate the precent of time this worked
    successrate = closedGap/totaldays
    risklist.pop(0)
    return mean(risklist), median, closedGap, totaldays, successrate