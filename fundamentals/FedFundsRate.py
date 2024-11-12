"""
Downloads the latest federal funds rate from st. Louis
"""
from fredapi import Fred

# Your FRED API key. Replace with your actual key.
# Here I used a file to fetch it automatically
with open('../passcodes/api_key_fred ', 'r') as f:
   api_key = f.read()

# Initialize Fred API with your key
fred = Fred(api_key=api_key)

# Fetch the Federal Funds Rate using the FRED series ID: 'FEDFUNDS'
fed_funds_rate = fred.get_series('FEDFUNDS')

# Display the latest rate
latest_rate = fed_funds_rate.iloc[-1]

print(f"Latest Federal Funds Rate: {latest_rate}")

# Optionally display the last few entries
print(fed_funds_rate.tail())


