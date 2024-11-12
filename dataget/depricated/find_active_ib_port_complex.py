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

#modules from this project
from dataget.ibkrApp import md
from dataget.ibkrApp import IBApp

#=====Essential objects=====#

def find_active_ib_port_complex(host=md.localhost, client=md.clientId) -> int:
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
    app = IBApp()
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