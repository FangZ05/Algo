from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from threading import Event
import time

class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connection_event = Event()

    def connectAck(self):
        # Triggered when the connection is successful
        print("Connected successfully.")
        self.connection_event.set()

    def error(self, reqId, errorCode, errorString):
        if errorCode == 502:  # Code 502 usually means connection failed
            print(f"Error {errorCode}: {errorString}")
            self.connection_event.set()  # To move on to the next port

    def disconnect_if_no_response(self):
        # Disconnect if the connection isn't acknowledged
        if not self.connection_event.is_set():
            self.disconnect()

def find_active_ib_port(app, host='127.0.0.1', client=123) -> int:
    """Attempt connection to common IBKR ports using ibapi to find an active one."""
    ports = [7497]  # Typical IBKR port options
    """
    for port in ports:
        print(f"Trying port {port}...")
        app.connect(host, port, client)
        app.connection_event.clear()  # Reset the event for each connection attempt
        
        # Wait for a response (success or error), with a timeout
        app.connection_event.wait(timeout=2)
        
        if app.isConnected():
            print(f"Active port found: {port}")
            return port
        else:
            app.disconnect_if_no_response()

    raise ConnectionError("No active IBKR Gateway or TWS port found.")
    """
    
    #iterate through all ports
    for port in ports:
        print(f"Trying port {port}...")
        app.connect(host, port, client)
        print(f"debug after connect, is connected: {app.isConnected()}")
        app.connection_event.clear()  # Reset the event for each connection attempt
        print(f"debug after clear, is connected: {app.isConnected()}")
        # Check multiple times within a timeout period
        connected = False
        for i in range(100):  # Retry up to 10 times
            print(f"current time: {i}, current connection:{app.isConnected()}")
            time.sleep(0.1)  # Check every 0.5 seconds
        # Wait for a response (success or error), with a timeout
        app.connection_event.wait(timeout=1)
        print(f"debug after wait, is connected: {app.isConnected()}")
        

        if app.isConnected():
            print(f"Active port found: {port}")
            return port
        else:
            app.disconnect_if_no_response()
            print(f"debug app.disconnect_if_no_response()")

    raise ConnectionError("No active IBKR Gateway or TWS port found.")
    
"""
def main():
    app = IBApp()
    active_port = None
    
    try:
        # Attempt to find the active port
        active_port = find_active_ib_port(app)
        print(f"Using active port: {active_port}")
        
        # Proceed with connection to the active port
        app.connect("127.0.0.1", active_port, clientId=123)
        
        # Add your IBAPI operations here (e.g., requesting data)
        time.sleep(2)  # To maintain the connection for demonstration

    except Exception as e:
        print(f"Error: {e}")
    finally:
        app.disconnect()
        print("Disconnected.")
        """