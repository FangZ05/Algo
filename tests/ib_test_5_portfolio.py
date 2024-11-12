from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading

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
from dataget.ibkrData import md

import datetime as dt
import dataget.ibkrData_initialize as ib

#initialize required variables
root_dir = md.root_dir #root directory
data_dir = md.data_dir #data directory
host = md.localhost #default host
client = md.clientId #default client
now = md.now #current time
lastexpr = md.lastexpr #last expiry date of interest


class IBApp(ib.IBApp):
    def __init__(self):
        ib.IBApp.__init__(self)
        self.portfolio_data = []

    def connect_app(self):
        self.connect(host, port, clientId=1)
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def disconnect_app(self):
        self.disconnect()

    def request_portfolio_data(self):
        """Request updates for account portfolio."""
        self.reqAccountUpdates(True, "U8798524")

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float,
                        marketValue: float, averageCost: float, unrealizedPNL: float,
                        realizedPNL: float, accountName: str):
        """Capture portfolio data in the callback."""
        portfolio_item = {
            'symbol': contract.symbol,
            'secType': contract.secType,
            'position': position,
            'marketPrice': marketPrice,
            'marketValue': marketValue,
            'averageCost': averageCost,
            'unrealizedPNL': unrealizedPNL,
            'realizedPNL': realizedPNL
        }
        self.portfolio_data.append(portfolio_item)
        #return (portfolio_item)
        print(portfolio_item)


    def accountDownloadEnd(self, account: str):
        """Called when all portfolio updates are sent."""
        print("Finished downloading portfolio.")
        self.disconnect_app()
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
        
    #app.connect_app()
    #app.request_portfolio_data()

