"""
Module for handling portfolio and watchlist management.
"""

class portfolio:
    #Portfolio itself
    def __init__(self, name, items):
        #give it a name
        self.name = name
        #get the itemized portfolio
        self.items = items
    
    #add item to the portfolio
    def add_items(self, tickers, shares):
        self.items[tickers] = shares


def make_portfolio(port={}, name="Default"):
    portclass = portfolio(name, port)
    return portclass
