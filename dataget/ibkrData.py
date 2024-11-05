"""
Crawing various data from IBKR
requires IBKR subscription
"""
if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

#import IBAPI
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

#use other modules within the project
from utilities.fileManagement import find_project_root

#other neccessary modules
from threading import Event #use multithreading & event handling
import time
import pandas as pd
from datetime import datetime
import datetime as dt
from threading import Thread
from pytz import timezone

#=====Essential objects=====#
class md():
    #metadata managements
    root_dir = find_project_root(project_name = 'algo')+'/' #get the root directory of this project
    tz = timezone('US/Eastern') #timezone 

    #define global variables
    localhost = '127.0.0.1' #localhost address
    clientId = 2 #clident ID that can be changed on the fly. 2 for datacrawling.
    port = 4001 #ID for IBKR port. Choose among [7497, 7496, 4002, 4001] 
                #to use designated port, otherwise use find_active_ib_port to detect it automatically
    ibkr_ports = [7497, 4001, 7496, 4002] #The list of TWS and Gateway ports
    now = datetime.now(tz=tz)


class IBApp(EWrapper, EClient):
    #define the IB class
    def __init__(self):
        EClient.__init__(self, self)
        self.option_data = [] #list of requested data for a contract
        self.df_option_chain = pd.DataFrame() #convert given data into dataframe
        self.connection_event = Event() #python's event handling, used manage connection
    #=================Connection detection================#
    def connectAck(self):
        # Triggered when the connection is successful
        super().connectAck()
        print("Connected successfully.")
        self.connection_event.set()

    def error(self, reqId:int, errorCode:int, errorString:str, advancedOrderRejectJson = ""):
        #call the original function first
        super().error(reqId, errorCode, errorString,
                      advancedOrderRejectJson = advancedOrderRejectJson)
        
        #terminate connection based on ranges of similar error codes in IB
        criticalerror = ((1100 <= errorCode < 2000) or #Connection related errors
                         (500 <= errorCode < 600)) #or # Critical system errors
                         #(2100 <= errorCode < 2200)) # Market data connection issues                                                       
        if criticalerror: 
            print(f"Critical Error {errorCode}: {errorString}")
            self.api_disconnect()
        

    def disconnect_event(self):
        # Disconnect if the there is no connection
        if not self.connection_event.is_set():
            self.api_disconnect()

    def api_disconnect(self):
            #disconnect from IBPAI
        try:
            self.connection_event.clear()
            self.disconnect()
            print("Disconnected from IBAPI.")
        except:
            print("Error disconnecting.")
        
    #=============Data Download====================#
    def option_contract(self, symbol, expr = md.now, monthly = False):
        """
        generate option contact based on the parameters given.
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"
        if monthly:
            expiry = self.dt_monthToStr(expr)
        else:
            expiry = self.dt_dayToStr(expr)
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
    def dt_dayToStr(self, t):
        #turns datetime to day string that can be parsed by contract.lastTradeDateOrContractMonth
        return t.strftime('%Y%m%d')
    
    def dt_monthToStr(self, t):
        #turns datetime to monthstring that can be parsed by contract.lastTradeDateOrContractMonth
        return t.strftime('%Y%m')
    
    def run_loop(self):
    #used for parallelization
        self.run()

def find_active_ib_port_complex(app, host=md.localhost, client=md.clientId) -> int:
    """
    Attempt connection to common IBKR ports using ibapi to find an active one.

    Input:
        app: the IBApp class that is associated with the request
        host: host server IP, default localhost
        clientId: the unique client ID of the API connection, default clientid
    Output:
        port: the port id of active ports.
    """
    ports = md.ibkr_ports
    active_ports = [] #The list of active ports in case there are multiple

    #iterate through all ports
    for port in ports:
        print(f"Trying port {port}...")
        app.connect(host, port, client)
        app.connection_event.clear()  # Reset the event for each connection attempt
        # Wait for a response (success or error), with a timeout
        app.connection_event.wait(timeout=1)
        if app.isConnected():
            print(f"Active port found: {port}")
            active_ports.append(port)
            app.api_disconnect()
        else:
            app.disconnect_event()

    #check if there are active ports
    if not active_ports:
        raise ConnectionError("No active IB Gateway or TWS port found.")
    
    # If multiple ports are open, prefer Gateway over TWS
    for port in [4001, 4002]:  # Check Gateway ports first
        if port in active_ports:
            print(f"Active Port is {port}.")
            return port
        
    print(f"Active Port is {active_ports[0]}.")
    return active_ports[0]  # Return first available port if no Gateway ports

def find_active_ib_port(app, host=md.localhost, client=md.clientId) -> int:
    """
    Attempt connection to common IBKR ports using ibapi to find an active one.

    Input:
        app: the IBApp class that is associated with the request
        host: host server IP, default localhost
        clientId: the unique client ID of the API connection, default clientid
    Output:
        port: the port id of active ports.
    """
    ports = md.ibkr_ports

    #iterate through all ports
    for port in ports:
        print(f"Trying port {port}...")
        app.connect(host, port, client)
        app.connection_event.clear()  # Reset the event for each connection attempt
        # Wait for a response (success or error), with a timeout
        app.connection_event.wait(timeout=1)
        if app.isConnected():
            print(f"Active port found: {port}")
            app.api_disconnect()
            return port
        else:
            app.disconnect_event()

    raise ConnectionError("No active IB Gateway or TWS port found.")
   
#==========functional functions==========#



#Download the data of a stock
def get_stock_data(ticker, timeframe, update = True,  p=md.root_dir+'data/', \
                   tz = md.tz, host = md.localhost, client = md.clientId):
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
                   tz = md.tz, host = md.localhost, client = md.clientId):
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
