"""
Caching data from IBKR so calls will be more efficient
Child module of ibkrData.py and ibkrData_options
"""
#neccessary python modules
from threading import Event #use multithreading & event handling
import time
import pandas as pd
from datetime import datetime
import datetime as dt
from threading import Thread
from dateutil.relativedelta  import relativedelta
from pathlib import Path
import os

if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

#import other modules within the project
from utilities.fileManagement import find_project_root
import dataget.ibkrData as ib
from dataget.ibkrApp import md


#initialize required variables
root_dir = md.root_dir #root directory
data_dir = md.data_dir #data directory
host = md.localhost #default host
client = md.client #default client
now = md.now #current time
lastexpr = md.lastexpr #last expiry date of interest

class IBApp(ib.IBApp):
    def __init__(self):
        ib.IBApp.__init__(self)
        self.option_data = [] #list of requested data for a contract
        self.df_option_chain = pd.DataFrame() #convert given data into dataframe
        self.contractReq_event = Event()

    # Callback to receive contract details
    def contractDetails(self, reqId, contr, verbose = False):
        print(f"Received contract details for "
              f"{contr.contract.symbol}"
              f"{contr.contract.strike}"
              f"{contr.contract.right} "
              f"{contr.contract.lastTradeDateOrContractMonth}")
        contract = contr.contract
        self.option_data.append({
            'conId': contract.conId,
            'symbol': contract.symbol,
            'secType': contract.secType,
            'expiry': contract.lastTradeDateOrContractMonth,
            'strike': contract.strike,
            'right': contract.right,  # Call or Put
            'multiplier': contract.multiplier,
            'exchange': contract.exchange,
            'primaryExchange': contract.primaryExchange,
            'currency': contract.currency,
            'tradingClass': contract.tradingClass,
            'includeExpired': contract.includeExpired,
            'secIdType': contract.secIdType,
            'secId': contract.secId,
            'description': contract.description,
            'issuerId': contract.issuerId,
            'localSymbol': contract.localSymbol,
            'full': contract
        })
    
    #Callback to signal the end of contract details
    def contractDetailsEnd(self, reqId):
        self.contractReq_event.set()
        self.df_option_chain = pd.DataFrame(self.option_data)
        print("Option chain received.")
        
    def failed_reqContract(self):
        # Disconnect if the request failed.
        if not self.contractReq_event.is_set():
            print("Contract Request Failed.")
            self.api_disconnect()
    
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=''):
        #call the original function first
        super().error(reqId, errorCode, errorString,
                      advancedOrderRejectJson = advancedOrderRejectJson)
        #handles in case of no security definition
        if errorCode == 200: #
            print(f"reqId {reqId} No Security Definition Error {errorCode}: {errorString}")
            self.contractReq_event.set()

    def get_option_chain_full(self, contract, reqId = 1):
        """
        Using reqContractDetails to get the option chain of a given date.
        """    
        # Request option chain
        ticker = contract.symbol
        expiry = contract.lastTradeDateOrContractMonth
        self.contractReq_event.clear() #initialize event by clearing
        print(f"Requesting data for {ticker}/{expiry}:")
        self.reqContractDetails(reqId, contract)


#Download the data of an option chain
def get_option_contracts(ticker, 
                         expr=[now, lastexpr],
                         monthly = True,
                         port = None,
                         host = host, 
                         client = client):
    '''
    Get the contract details of options chain for the specified ticker.
    
    Input:
        see save_contract_details.
    
    Output:
        app.df_option_chain: a dataframe of option contract details with 
                            full contract details, symbol, expiry date, 
                            strike, and rights.
        
    '''
    #generate and IBApp object
    app = IBApp()
    try:
        #generate a list of contracts of interest
        contracts = []
        if monthly:
            #check if we'd like to request option by the day or month
            months = 12 * (expr[-1].year - expr[0].year) + (expr[-1].month - expr[0].month) + 1
            period = range(months)
            for i in period:
                #iterate over all month
                date = expr[0] + relativedelta(months = i)
                contract = app.option_contract(ticker, expr = date, monthly = True)
                contracts.append(contract)
                
        else:
            period = range((expr[-1] - expr[0]).days)
            for i in period:
                date = expr[0] + dt.timedelta(days=i)
                contract = app.option_contract(ticker, expr = date, monthly = False)
                contracts.append(contract)
            
        #connect to IBAPI by detecting the active port
        
        if not port:
            port = ib.autoport(app)
        app.api_run(port)
        
        for i, contr in enumerate(contracts):
            app.get_option_chain_full(contr, reqId=i+1)

            app.contractReq_event.wait(timeout=120)
            app.failed_reqContract()
        
        
        
    except Exception as e:
        #terminate the process if an error occurred
        print(f"Error: {e}")
    finally:
        #always join thread and disconnect api after everything
        app.api_disconnect()
        print("End of Operation.")
        
    return app.df_option_chain
    #========================================================#
def save_contract_details (ticker,
                            data_dir = data_dir,
                            expr=[now, lastexpr],
                            monthly = True,
                            port = None,
                            host = host, 
                            client = client):
    '''
    Save the contract details of options chain for the specified ticker.
    
    Input:
        ticker: stock's ticker symbol.
        data_dir: directory for saving all data.
        expr: specifies the range of date of the contract.
            default [now, lastexpr], specified in ibkrData.py/metadata. 
        monthly: whether to request the data by month or by day.
            default True
        port: specify the IB connection port (TWS or IBGateway)
            default None, where the function would detect active port automatically.
        host: specify the IB host.
        client: specify the IB client ID.
        
    Output:
        None
    Results:
        saves the contract details into a .csv file that can be accessed later.
    '''
    #make sure the tickers is capitalized, for style
    ticker = ticker.upper()
    
    #grab the necessary contract details
    contract_details = get_option_contracts(ticker, expr=expr, 
                                            monthly=monthly, port=port, 
                                            host=host, client=client)
    #sort the data by date
    contract_details = contract_details.sort_values('expiry', ascending = False, ignore_index=True)
    
    #get target file
    path = f"{data_dir + ticker}/options/" #path str of options directory
    dirpath = Path(path) #path object the the options directiory
    targetfile = f"{path}/{ticker}_contracts.csv" #path str of contract details files
    
    #check if the path exist, create the path if not
    if not dirpath.exists():
        os.makedirs(dirpath)
    print(f"Exporing file {ticker}_contracts.csv...")
    contract_details.to_csv(targetfile, index=False)
    print(f"Saved File {ticker}_contracts.csv.")
    
if __name__ == '__main__':
    #debugging script
    app = IBApp()
    
    port = 4001
    ticker = 'TSLA'
    date=md.now
    contracts = []
    for i in range((lastexpr-now).days):
        date = md.now + dt.timedelta(days=i)
        contract = app.option_contract(ticker, expr = date)
        contracts.append(contract)