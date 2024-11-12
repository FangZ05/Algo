"""
Crawing various data from IBKR

Requires IBKR market subscription
Requires logged in TWS or IBGateway

Child module of ibkrApp
"""
if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

#modules from Python
from threading import Event #use multithreading & event handling
import time
import pandas as pd
from datetime import datetime
import datetime as dt
from threading import Thread

#modules from IBAPI
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

#modules from this project
from utilities.fileManagement import find_project_root
from dataget.ibkrApp import md
from dataget.ibkrApp import IBApp as parentIBApp
from dataget.ibkrApp import find_active_ib_port

#=====Essential objects=====#


class IBApp(parentIBApp):
    #define the IB class
    def __init__(self):
        parentIBApp.__init__(self)
        self.option_data = [] #list of requested data for a contract
        self.df_option_chain = pd.DataFrame() #convert given data into dataframe
        self.connection_event = Event() #python's event handling, used manage connection
        
    #=============Data Download====================#
    def option_contract(self, symbol, secType = md.secType,
                        exchange = md.exchange, currency = md.currency,
                        expr = md.now, monthly = False):
        """
        generate option contact based on the parameters given.
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = currency
        if monthly:
            expiry = md.dt_monthToStr(expr)
        else:
            expiry = md.dt_dayToStr(expr)
        contract.lastTradeDateOrContractMonth = expiry
        return contract
    
    # Callback to receive contract details
    def contractDetails(self, reqId, contr):
        print(f"Received contract details for \
              {contr.contract.symbol} \
              {contr.contract.lastTradeDateOrContractMonth} \
                  {contr.contract.strike} \
                      {contr.contract.right}")
        contract = contr.contract
        self.option_data.append({
            'Symbol': contract.symbol,
            'Expiry': contract.lastTradeDateOrContractMonth,
            'Strike': contract.strike,
            'Right': contract.right  # Call or Put
        })
    
    #Callback to signal the end of contract details
    def contractDetailsEnd(self, reqId):
        print("Option chain received.")
        self.df_option_chain = pd.DataFrame(self.option_data)
        self.api_disconnect()
    
    
    def get_option_chain(self, symbol, date, strike = 0.0, reqId = 1):
        """
        Using reqContractDetails to get the option chain of a given date.
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"
        contract.strike = strike
    
        # Request option chain
        print(f"Requesting data for {contract.symbol}:")
        self.reqContractDetails(reqId, contract)
    
    
    #=====essential functions=====#


   
#==========functional functions==========#



#Download the data of a stock
def get_stock_data(ticker, timeframe, update = True,  p=md.root_dir+'data/', \
                   tz = md.tz, host = md.localhost, client = md.client):
    '''
    Get the data for specified ticker.

    Input:
        ticker: stock's ticker symbol.
        update: Force update. Default true.
        p: pathway to data folder.
        tz: Timezone of the output data.
    '''
    app = IBApp()
    try:
        #connect to IBAPI by either mannually or automatically selecting a port
        if md.port in md.ibkr_ports:
            port = md.port
        else:
            port = find_active_ib_port(app)
        app.connect(host, port, client)

    
    except Exception as e:
        #terminate the process if an error occurred
        print(f"Error: {e}")
    finally:
        #always disconnect after everything
        app.api_disconnect()
        print("Disconnected.")

    #========================================================#

#Download the data of an option chain
def get_option_data(ticker, expiry, p=md.root_dir+'data/', \
                   tz = md.tz, host = md.localhost, client = md.client):
    ''''
    Get the data for specified ticker.

    Input:
        ticker: stock's ticker symbol.
        update: Force update. Default true.
        p: pathway to data folder.
        tz: Timezone of the output data.
    '''
    #generate and IBApp object
    app = IBApp()
    try:
        #connect to IBAPI by detecting the active port
        port = find_active_ib_port(app)
        app.connect(md.localhost, port, client)
        
        api_thread = Thread(target=app.run_loop, args=(app,), daemon=False)
        api_thread.start()

        # Fetch option chain for TSLA
        app.get_option_chain(1, "TSLA")
        
    except Exception as e:
        #terminate the process if an error occurred
        print(f"Error: {e}")
    finally:
        #always disconnect after everything
        app.api_disconnect()
        print("Disconnected.")
    #========================================================#
