"""
Downloads the risk-free rate, i.e. the 13 week/3 month T-bill yield using yfinance
"""

import yfinance as yf
from pathlib import Path
import os
from datetime import datetime as dt

def risk_free_rate(verbose=False, update=False):
    #write a function for fetching the rate
    def download_rate():
        # Define the treasury ticker symbols
        tickers = "^IRX"  # 13-week treasury yields
        # Download treasury yield data
        treasury_data = yf.download(tickers, period="1d", interval="1d")
        
        # Display the latest yields
        latest_data = treasury_data['Close'].iloc[-1]
        return latest_data
    
    #check if the data exist
    targetfile = "risk_free_rate"
    targetpath = Path(targetfile)
    if targetpath.exists():
        # Get the file's last modification time
        file_mod_time = os.path.getmtime(targetfile)
        file_mod_time = dt.fromtimestamp(file_mod_time)
        
        # Get the current time
        current_time = dt.now()

        # Calculate the difference in days
        delta_days = (current_time - file_mod_time).days
        
        # if last updated more than 1 day ago, download latest rate
        if delta_days > 1 or update:
            rate = download_rate()
            with open(targetfile, 'w') as file:
                file.write(f'{rate}')
        
        #otherwise grab the rate directly
        else:
            with open(targetpath, 'r') as f:
               rate = float(f.read())

        if verbose:
            print(f"\n Current Risk Free Rate:{rate:.2f}")
        return rate
    
    #download the rate otherwise
    else:
        rate = download_rate()
        with open(targetfile, 'w') as file:
            file.write(f'{rate}')
        if verbose:
            print(f"\n Current Risk Free Rate:{rate:.2f}")
        return rate

if __name__ == '__main__':
    #for debugging
    rate = risk_free_rate()
    print("\n This is a debugging message for riskFreeRate.py. You should not see this.")

