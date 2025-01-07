"""
Downloads options data from IBKR

Child module of ibkrData.py
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
import ibapi
import pandas as pd
import numpy as np


from threading import Thread
from threading import Event, Lock #use multithreading & event handling
import time
from pathlib import Path


if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

#import other modules within the project
from utilities.fileManagement import find_project_root
import dataget.ibkrData as ib
from dataget.ibkrApp import md #metadata
from dataget.ibkrApp import autoport
from dataget.ibkrData_initialize import save_contract_details


#initialize required variables
data_dir = md.data_dir
host = md.localhost
client = md.client #default clients


class IBApp(ib.IBApp):
    def __init__(self):
        ib.IBApp.__init__(self)
        self.market_data = {} #list of requested data for a contract
        self.market_greek = {}
        self.market_oi = {}
        self.DataReq_event = Event()
        self.data_lock = Lock()
    
    
    def request_options_data(self, reqId, contract):
        """
        Request open interest and greek of an option contract.
        """
        #initialize marekt data returns
        
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
            
        self.market_data[reqId]['ticker'] = contract.symbol
        self.market_data[reqId]['expiry'] = contract.lastTradeDateOrContractMonth
        self.market_data[reqId]['strike'] = contract.strike
        self.market_data[reqId]['right'] = contract.right
        self.market_data[reqId]['open_interest'] = 0
        
        #generate separate tracker ID for OI request and greek request
        tracker_id = reqId*2 #double the id space for two requests 
        #self.request_options_openInterest(tracker_id, contract)
        self.request_options_greeks(tracker_id + 1, contract)
        
        print(f"requesting market data for {contract.symbol} {contract.strike}{contract.right}: {contract.lastTradeDateOrContractMonth}")
    def request_options_openInterest(self, tracker_id, contract):
        """
        Request open interest for an options contract using live method.
        """
        self.reqMarketDataType(1) #live data
        self.reqMktData(tracker_id, 
                        contract, 
                        "101", 
                        False, 
                        False, 
                        [])
    
    def request_options_greeks(self, tracker_id, contract):
        """
        Request market data for an options contract using frozen method.
        """
        self.reqMarketDataType(2) #live or frozen data

        # Request market data with the `snapshot=False` to get continuous updates
        
        self.reqMktData(tracker_id, 
                        contract, 
                        "100, 101, 104, 106", 
                        False, 
                        False, 
                        [])
        
    #def marketDataType(self, reqId: int, marketDataType:int):
    #    self.market_data[reqId]['dataType'] = marketDataType
    #    print("MarketDataType. ReqId:", reqId, "Type:", marketDataType)
        
    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: int):
        with self.data_lock:
            if reqId not in self.market_greek:
                self.market_greek[reqId] = {}
            
            if tickType in [TickTypeEnum.BID, TickTypeEnum.ASK, TickTypeEnum.LAST]:
                self.market_greek[reqId][TickTypeEnum.toStr(tickType)] = price
                print(f"Price update for ticker {reqId} - {TickTypeEnum.toStr(tickType)}: {price}")
                 


    def tickOptionComputation(self, reqId: int, 
                              tickType: int, tickAttrib:int,
                              impliedVol: float, delta: float,
                              optPrice: float, pvDividend: float,
                              gamma: float, vega: float,
                              theta: float, undPrice: float):
        
        with self.data_lock:
            if reqId not in self.market_greek:
                self.market_greek[reqId] = {}
    
            # Store the Greeks
            if tickType == TickTypeEnum.MODEL_OPTION:
                self.market_greek[reqId].update({
                "Delta": delta,
                "Gamma": gamma,
                "Theta": theta,
                "Implied Volatility": impliedVol
                })
                print(f"Greeks update for ticker {reqId} - "
                      f"Delta: {delta:.2f}, Gamma: {gamma:.2f}"
                      f"Theta: {theta:.2f}")
             
    def tickSize(self, reqId: int, tickType: int, size: int):
        with self.data_lock:
            if reqId not in self.market_oi:
                self.market_oi[reqId] = {}
                self.market_oi[reqId]['open_interest'] = 0
                
            print(f"request tickSize for {reqId}: type {tickType}")
            # Map tick types to meaningful names
            open_interest = [27, 28] #27 for call OI, 28 for put OI
            if tickType in open_interest:  # Option Call Open Interest
                self.market_oi[reqId]['open_interest'] += size
                print(f"OI update for ticker {reqId} - +{size}")
            
                    
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
        tgt_date = int(md.dt_dayToStr(md.now))
    
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
            port = ib.find_active_ib_port(app)
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
    ticker = 'TSLA'
    contract_details = get_option_contracts(ticker)
    contracts = contract_from_df(contract_details)

    
    app = IBApp()
    port = 7497
    #app.api_run()
    def run_req(lst):
        #app.reqMarketDataType(1)
        for i, contract in enumerate(lst):
            reqId = i+1
            app.request_options_data(reqId, contract)
            #app.request_options_openInterest(reqId, contract)
            
    #app.connect("127.0.0.1", 7497, clientId=1)
    #thread = Thread(target=app.run, daemon=True)
    #thread.start()
    #app.request_Data(contract_list)
    #pd.DataFrame(app.market_data).transpose()

