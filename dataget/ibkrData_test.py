import socket
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from threading import Event
from threading import Thread
import time
import pandas as pd
from ibapi.contract import Contract
from contextlib import contextmanager
from ibapi.ticktype import TickTypeEnum

#define global variables
localhost = '127.0.0.1' #localhost address
clientid = 1 #clident ID that can be changed on the fly

class IBApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.option_data = []
        self.df_option_chain = pd.DataFrame()
        
    
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
        self.disconnect()
    
    # Fetch option chain details
    def get_option_chain(self, reqId, symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "OPT"
        contract.exchange = "SMART"
        contract.currency = "USD"

        # Request option chain
        self.reqContractDetails(reqId, contract)
		
def run_loop(app):
    app.run()

@contextmanager
def socket_context(host: str, port: int, timeout: float = 1.0):
    """Context manager for safe socket handling"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        yield sock
    finally:
        sock.close()

def is_port_open(host: str, port: int) -> bool:
    """Check if a port is open with proper resource cleanup"""
    try:
        with socket_context(host, port) as sock:
            sock.connect((host, port))
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def find_active_ib_port(host: str = localhost) -> int:
    """
    Find active IB port
    
    Input:
        host: host server of the port, default localhost
    """
    ports = [7497, 7496, 4002, 4001]  # TWS (live/paper) and IB Gateway (live/paper)
    
    active_ports = []
    threads = []
    
    def check_port(port):
        nonlocal active_ports
        if is_port_open(host, port):
            print(f"Port {port} is open")
            active_ports.append(port)

    for port in ports:
        thread = Thread(target=check_port, args=(port,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if not active_ports:
        raise ConnectionError("No active IB Gateway or TWS port found.")
    
    # If multiple ports are open, prefer Gateway over TWS
    for port in [4001, 4002]:  # Check Gateway ports first
        if port in active_ports:
            return port
    
    return active_ports[0]  # Return first available port if no Gateway ports


#port = find_active_ib_port()
"""
# Create the application object
app = IBApp()

# Connect to TWS or IB Gateway 

app.connect(localhost, port, clientId=clientid)


# Launch a separate thread to run the message loop
api_thread = Thread(target=run_loop, args=(app,), daemon=True)
api_thread.start()
time.sleep(2)
print(f'debug message')
api_thread.join()

app.disconnect()
"""
"""
def main():
    app = IBApp()

    try:
        # Find the active port (TWS or IB Gateway)
        active_port = find_active_ib_port()
        print(f"Connecting to IB on port {active_port}")
        
        # Connect to the active port
        app.connect("127.0.0.1", active_port, clientId=123)
        
        # Do IBAPI operations
        app.req_completed.wait()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        app.disconnect()

if __name__ == "__main__":
    main()
    """