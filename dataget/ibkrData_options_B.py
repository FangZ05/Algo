"""
Downloads options data from IBKR

Child module of ibkrData.py
"""
if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)
    
    from technicals.options import GEX
    from technicals.options import GEX_keylevel
    from technicals.options import expected_move
    
#modules from Python
import pandas as pd
import numpy as np
from threading import Thread, Event, Lock #use multithreading & event handling
import time
import datetime as dt
from pathlib import Path

#modules from IBAPI
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum

#modules from this project
import dataget.ibkrData as ib
from dataget.ibkrApp import md #metadata
from dataget.ibkrApp import autoport
from dataget.ibkrData_initialize import save_contract_details
from utilities.utilities_general import is_odd, is_even
import technicals.options


#initialize required variables
data_dir = md.data_dir
host = md.localhost
client = md.client #default clients
port = 7497
#port = autoport()
timeout = md.timeout
#timeout = 120

class IBApp(ib.IBApp):
    def __init__(self):
        ib.IBApp.__init__(self)
        self.market_data_df = pd.DataFrame()
        self.market_data = {} #list of requested data for a contract
        self.market_greek = {} #greek data
        self.market_oi = {} #OI data
        
        self.dataReq_event_oi = Event() #end of req OI event
        self.dataReq_event_greek = Event() #end of req options greek event
        
        #initialize required variables
        self.req_length = 0
        
        self.data_lock = Lock() #anti-racing for multithreading
        
    #===========Event Management Functions==========#
    def dataReq_event_oi_failed(self):
        # Disconnect if the request failed.
        if not self.dataReq_event_oi.is_set():
            print("Contract Request Failed.")
            #self.api_disconnect()
            
    def dataReq_event_greek_failed(self):
        # Disconnect if the request failed.
        if not self.dataReq_event_greek.is_set():
            print("Contract Request Failed.")
            #self.api_disconnect()
            
    #==========Data Request Functions==========#
    def request_options_data(self, contracts):
        """
        Request open interest and greek of a list of option contract.
        """

        
        with self.data_lock:
            self.api_run(port)
            
            #initiate the contracts in market_data
            for i, contract in enumerate(contracts):
                tracker_id = i+1
                #initialize marekt data returns
                self.initialize_market_data(tracker_id, contract)
                
                #print(f"requesting market data for {contract.symbol} {contract.strike}{contract.right}: {contract.lastTradeDateOrContractMonth}")
            
            #get the request length
            self.req_length = len(self.market_data)
        
        #get the open interest of contracts
        self.reqMarketDataType(1) #live data
        self.dataReq_event_oi.clear() #initialize event by clearing

        for i, contract in enumerate(contracts):
            #generate separate tracker ID for OI request
            reqId = (i+1)*2 #uses even number of OI
            
            
            self.reqMktData(reqId, contract, "101", 
                            False, False, [])
            print(f"{reqId}: requesting OI for {contract.symbol} {contract.strike}{contract.right}: {contract.lastTradeDateOrContractMonth}")
        
        #wait until a signal indicates the end of req OI
        self.dataReq_event_oi.wait(timeout=timeout)
        self.dataReq_event_oi_failed()
        
        #get the options greek of contracts
        self.reqMarketDataType(2) #live or frozen data
        self.dataReq_event_greek.clear() #initialize event by clearing
        

        for i, contract in enumerate(contracts):
            #generate separate tracker ID for greek request
            reqId = (i+1)*2 + 1 #uses odd number of greeks
            
            self.reqMktData(reqId, contract, "100, 104, 106", 
                            False, False, [])
            print(f"{reqId}: requesting greeks for {contract.symbol} {contract.strike}{contract.right}: {contract.lastTradeDateOrContractMonth}")
        
        #wait until a signal indicates the end of req greeks
        self.dataReq_event_greek.wait(timeout=timeout)
        self.dataReq_event_greek_failed()
        
        print("Successfully retried market data.")

        #disconnect once done
        self.api_disconnect()
        
        #process the data into proper dataframe
        contract_df = pd.DataFrame(self.market_data).transpose()
        
        oi_df = pd.DataFrame(self.market_oi).transpose()
        oi_df['open_interest'] = oi_df['call_open_interest'] + oi_df['put_open_interest']
        
        greek_df = pd.DataFrame(self.market_greek).transpose()
        greek_df['BID'] = greek_df['BID'].replace(-1, np.nan)
        greek_df['ASK'] = greek_df['ASK'].replace(-1, np.nan)
        greek_df['MID'] = (greek_df['ASK'] + greek_df['BID']) / 2
        greek_df = greek_df.fillna(0)
        
        dfs = [contract_df, oi_df['open_interest'], greek_df]
        market_data_df = pd.concat(dfs, axis = 1)
        
        return market_data_df
       
    
    def initialize_market_data(self, tracker_id, contract):
        """
        creates a entry in market_data corresponding to an contract 
        """
        if tracker_id not in self.market_data:
            self.market_data[tracker_id] = {}
            
        self.market_data[tracker_id]['ticker'] = contract.symbol
        self.market_data[tracker_id]['expiry'] = contract.lastTradeDateOrContractMonth
        self.market_data[tracker_id]['strike'] = contract.strike
        self.market_data[tracker_id]['right'] = contract.right
    

        
    #==========IBAPI Callback Functions==========#      
    def tickSize(self, reqId: int, tickType: int, size: int):
        #ignore cases where OI is not required
        if is_even(reqId):
            #convert reqId back to tracker_id
            tracker_id = int(reqId/2)
            
            with self.data_lock:               
                if tracker_id not in self.market_oi:
                    self.market_oi[tracker_id] = {}
                    self.market_oi[tracker_id]['call_open_interest'] = 0
                    self.market_oi[tracker_id]['put_open_interest'] = 0
                    
                #check if tickType is OI, 27 for call OI, 28 for put OI
                if tickType == 27:  
                    #call option open interest        
                    self.market_oi[tracker_id].update({
                        'call_open_interest': size
                        })
                    print(f"OI update for tracker_id {tracker_id} - call OI:{size}")
                    
                elif tickType == 28:
                    #put option open interest                 
                    self.market_oi[tracker_id].update({
                        'put_open_interest': size
                        })
                    print(f"OI update for tracker_id {tracker_id} - put OI:{size}")
                    
                    
                ###print(f"debug tickType {tickType} update for ticker {tracker_id} - {size}")
                ###print(f"debug: req_len:{self.req_length}, oi: {len(self.market_oi)}")
                
                if (len(self.market_oi) >= self.req_length) and not self.dataReq_event_oi.is_set():
                    #end of request once all data has a request
                    self.dataReq_event_oi.set()
                    time.sleep(1)

            
    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: int):
        #ignore cases where price is not required
        if is_odd(reqId):
            #convert reqId back to tracker_id
            tracker_id = int((reqId - 1)/2)
            
            #ignore if greek is not required
            with self.data_lock:
                if tracker_id not in self.market_greek:
                    self.market_greek[tracker_id] = {}
                
                if tickType in [TickTypeEnum.BID, TickTypeEnum.ASK, TickTypeEnum.LAST]:
                    self.market_greek[tracker_id][TickTypeEnum.toStr(tickType)] = price
                    print(f"Price update for ticker {tracker_id} - {TickTypeEnum.toStr(tickType)}: {price}")
                    
    
    def tickOptionComputation(self, reqId: int, 
                              tickType: int, tickAttrib:int,
                              impliedVol: float, delta: float,
                              optPrice: float, pvDividend: float,
                              gamma: float, vega: float,
                              theta: float, undPrice: float):
        #ignore if greek is not required
        if is_odd(reqId):
            #convert reqId back to tracker_id
            tracker_id = int((reqId - 1)/2)
            
            with self.data_lock:
                if tracker_id not in self.market_greek:
                    self.market_greek[tracker_id] = {}
        
                # Store the Greeks
                if tickType == TickTypeEnum.MODEL_OPTION:
                    #ignore unneccessary tickType and when greek is not needed
                    self.market_greek[tracker_id].update({
                    "Delta": delta,
                    "Gamma": gamma,
                    "Theta": theta,
                    "Implied Volatility": impliedVol
                    })
                    print(f"Greeks update for tracker_id {tracker_id} - "
                          f"Delta: {delta:.2f}, Gamma: {gamma:.2f} "
                          f"Theta: {theta:.2f}, impliedVol: {impliedVol:.2f}")
                    
                    ###print(f"debug: req_len:{self.req_length}, greek: {len(self.market_greek)}")
                    if (len(self.market_greek) >= self.req_length) and not self.dataReq_event_greek.is_set():
                        #end of request once all data has a request
                        self.dataReq_event_greek.set()

             

    

            
                    
def get_option_contracts(ticker, expr = None, data_dir = data_dir, update = False):
    """
    Get the required options' contract.
    
    
    """
    
    #get the data path and targetfile
    contractpath = f"{data_dir + ticker}/options/"
    filepath = f"{contractpath}/{ticker}_contracts.csv"
    targetfile = Path(filepath)
    
    #get the target date if given, or use the current time if not
    if expr:
        tgt_date = int(expr)
    else:
        tgt_date = int(md.dt_dayToStr(md.now+dt.timedelta(8/24))) #+8hr in case of after market close
    
    if not update:
        #check if the file needs update
        if targetfile.exists():
            print(f"Contracts for {ticker} found.")
            #force update if file is outdated
            header = pd.read_csv(targetfile, nrows = 1)
            if header['expiry'].iloc[0] < tgt_date:
                print(f"Contracts for {ticker} is outdated.")
                update = True
        else:
            #force update if file does not exist
            print(f"Contracts for {ticker} not found.")
            update = True
    
    #update the contract details
    if update:
        print("Updating contract details...")
        save_contract_details(ticker)
        
    
    #load the contract details as dataframe
    contract_details = pd.read_csv(targetfile)
    
    #fill nan that are supposed to be empty string
    nan_cols = ['primaryExchange', 'secIdType', 'secId', 'description', 'issuerId']
    contract_details[nan_cols] = contract_details[nan_cols].fillna('')
    
    #filter the dataframe to the first expiry date after target date
    exprDates = contract_details['expiry'].unique() #get unique expiry dates
    exprDates = exprDates[exprDates >= tgt_date] #filter to only dates after target date
    expiry = exprDates.min() #find the target expiry
    
    #filter the data to only the target expiry
    contract_details = contract_details.drop(
                contract_details[contract_details['expiry'] != expiry].index)
    #sort the results by strike
    contract_details = contract_details.sort_values('strike', ascending = False)

    
    return contract_details

def contract_from_df(dataframe):
    """
    Turn a contracts dataframe into a list of ibapi.contract object.
    Input:
        dataframe: a dataframe of contracts.
    Output:
        contract_list -> list: a list of contract objects from the dataframe.
    """
    contract_list = []

    for i in dataframe.itertuples():
        #Set the contract properties
        contract = Contract()
        contract.conId = int(i.conId) if i.conId else 0
        contract.symbol = i.symbol
        contract.secType = i.secType
        contract.lastTradeDateOrContractMonth = i.expiry
        contract.strike = float(i.strike) if i.strike else 0.0
        contract.right = i.right
        contract.multiplier = i.multiplier
        contract.exchange = i.exchange
        contract.primaryExchange = i.primaryExchange
        contract.currency = i.currency
        contract.localSymbol = i.localSymbol
        contract.tradingClass = i.tradingClass
        contract.includeExpired = i.includeExpired
        
        #save to a list
        contract_list.append(contract)
        
    return contract_list
    
def req_option_data(ticker, 
                    expr = None, 
                    data_dir = data_dir, 
                    update = False,
                    port = None,
                    host = host, 
                    client = client):
    app = IBApp()
    options = pd.DataFrame()
    try:
        contract_details = get_option_contracts(ticker, expr = expr, data_dir = data_dir, update = False)
        contract_list = contract_from_df(contract_details) 
        
        if not port:
            port = autoport()
        app.connect(host, port, client)
        
        #generate a main thread
        api_thread = Thread(target=app.run_loop, daemon=False)
        api_thread.start()
        time.sleep(0.1) #small pause to make sure there is no race
        
        app.reqMarketDataType(4)
        app.request_Data(contract_list)
        
        app.DataReq_event.wait(timeout=120)
        app.failed_reqContract()
        
        options = pd.DataFrame(app.market_data).transpose()
    finally:
        #always join thread and disconnect api after everything
        app.api_disconnect()
        if api_thread:
            api_thread.join() #end of threaded operation
        print("End of Operation.")
        
    return options



if __name__ == "__main__":
    print("hello world")
    ticker = 'SPX'
    contract_details = get_option_contracts(ticker)
    contracts = contract_from_df(contract_details)
    price = 6002.46
    
    app = IBApp()
    #port = 4001
    #app.api_run()

    data = app.request_options_data(contracts)
    GEX(data)
    key_level = GEX_keylevel(data)
    exp_move = expected_move(price, data, verbose=True)
    
    #app.contractReq_event.wait(timeout=120)
    #app.connect("127.0.0.1", 7497, clientId=1)
    #thread = Thread(target=app.run, daemon=True)
    #thread.start()
    #app.request_Data(contract_list)
    #pd.DataFrame(app.market_data).transpose()

