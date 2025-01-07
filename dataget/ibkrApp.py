"""
Codes for managing IBAPI

Requires IBKR market subscription
Requires logged in TWS or IBGateway

Including metadata, running, connecting
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
import datetime as dt
from datetime import datetime
from pytz import timezone
from threading import Thread
from threading import Event
import time

#modules from IBAPI
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

#modules from this project
from utilities.fileManagement import find_project_root

class md():
    #metadata and functions used for metadata management
    
    #file management
    root_dir = find_project_root(project_name = 'algo')+'/' #get the root directory of this project
    data_dir=root_dir+'data/' #get the data directory
    

    #connection variables
    localhost = '127.0.0.1' #localhost address
    client = 2 #clident ID that can be changed on the fly. 2 for datacrawling.
    
    port = 4001 #ID for IBKR port. Choose among [7497, 7496, 4002, 4001] 
                #to use designated port, otherwise use find_active_ib_port to detect it automatically
    ibkr_ports = [4001, 7497, 4002, 7496] #The list of TWS and Gateway ports, prioritize Live account and IBGateway
    timeout = 120 #timeout time in seconds
    

    #define contract metadata
    secType = 'OPT'
    exchange = 'SMART'
    currency = 'USD'

    #time variables
    tz = timezone('US/Eastern') #timezone 
    now = datetime.now(tz=tz)
    is_marketopen = (now.time() > dt.time(9, 30)) and (now.time() < dt.time(16))
        #check if the market is open
        
    lastexpr = now + dt.timedelta(days=7) #last expiry date of interest, default 7 days from now
    
    #date conversion functions
    def days_since_AD(date):
        #converts date in integer to days since AD
        if date < 1000000:
            date = date * 100 + 1 #if the date is given in monthly
        year = date // 10000
        month = (date % 10000) // 100
        day = date % 100
        # Normalize days for each year, month, and day
        days = year * 365 + (year // 4) - (year // 100) + (year // 400)  # Approximate leap years
        days += sum([31, 28 + (1 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 0), 
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][:month - 1])  # Add month days
        days += day
        return days
    
    def dt_dayToStr(t):
        #turns datetime to day string that can be parsed by contract.lastTradeDateOrContractMonth
        return t.strftime('%Y%m%d')
    
    def dt_monthToStr(t):
        #turns datetime to monthstring that can be parsed by contract.lastTradeDateOrContractMonth
        return t.strftime('%Y%m')

class IBApp(EWrapper, EClient):
    #define the IB class
    def __init__(self):
        EClient.__init__(self, self)
        self.connection_event = Event() #python's event handling, used manage connection
        self.current_thread = [] #currently running thread

    #=================Connection detection================#
    def connectAck(self):
        # Triggered when the connection is successful
        super().connectAck()
        print("Connected successfully.")
        self.connection_event.set()

    def disconnect_event(self):
        # Disconnect if the there is no connection
        if not self.connection_event.is_set():
            self.api_disconnect()

    #===============Connection Management====================#
    def api_connect(self, host = md.localhost, port = md.port, client = md.client):
        """
        Connect to IBAPI.
        """
        self.connect(host, port, client)

    def api_run(self, port = md.port):
        """
        run the app on a separate thread.
        """
        self.api_connect(port = port)
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        self.current_thread.append(thread)
        
        time.sleep(0.1) #small pause to make sure there is no race

    def api_disconnect(self):
        #disconnect from IBPAI, clear connection event, and join any running thread
        try:
            self.connection_event.clear()
            self.disconnect()
            print("Disconnected from IBAPI.")

            for i in self.current_thread:
                i.join()
                print(f"{i} has joined the main thread.")
            self.current_thread = []
        except:
            print("Error disconnecting.")

    #=====Error Handling======#
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

def autoport(app = IBApp(), host=md.localhost, client=md.client) -> int:
    """
    Attempt connection to common IBKR ports using ibapi to find an active one.

    Input:
        app: the IBApp class that is associated with the request
        host: host server IP, default localhost
        clientId: the unique client ID of the API connection, default clientid
    Output:
        port: the port id of active ports.

    Note: See find_active_ib_port_complex() in depricated/ for a more complex version 
            that prioritize IBgateway ports at the cost of speed
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
