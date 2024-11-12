#python
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickType
import threading

if __name__ == '__main__':
    #mimics relative import when run as a script
    import os
    import sys
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)
    
from dataget.ibkrData_options import get_option_contracts
class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.option_data = {}

    def start(self, contracts):
        """Request market data for a list of contracts."""
        self.next_ticker_id = 1
        for contract in contracts:
            ticker_id = self.next_ticker_id
            self.next_ticker_id += 1
            self.option_data[ticker_id] = {}
            # Request market data with the `snapshot=False` to get continuous updates
            self.reqMktData(ticker_id, contract, "", False, False, [])

    def tickPrice(self, reqId, tickType, price, attrib):
        """Handle bid, ask, and last prices."""
        if tickType in [TickType.BID, TickType.ASK, TickType.LAST]:
            self.option_data[reqId][TickType.getField(tickType)] = price
            print(f"Price update for ticker {reqId} - {TickType.getField(tickType)}: {price}")

    def tickOptionComputation(self, reqId, tickType, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        """Handle option Greeks and open interest."""
        if tickType == TickType.MODEL_OPTION:
            self.option_data[reqId].update({
                "Delta": delta,
                "Gamma": gamma,
                "Theta": theta,
                "Implied Volatility": impliedVol
            })
            print(f"Greeks update for ticker {reqId} - Delta: {delta}, Gamma: {gamma}, Theta: {theta}")


# Example usage:
if __name__ == "__main__":
    app = IBApp()

    # Create your contracts
    contract_details = get_option_contracts('TSLA')
    contracts = contract_details['Full'].values
    
    

    # Connect and request data
    #app.connect("127.0.0.1", 4001, clientId=1)
    #app.start(contracts)

    # Start the socket in a new thread
 
    #thread = threading.Thread(target=app.run, daemon=True)
    #thread.start()