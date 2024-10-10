import indicators as h

def main():
    #get ticker
    #ticker = input("Enter Stock symbol")
    #ticker = input("Enter Stock Ticker")
    ticker = "AMD"

    #path to stock data
    path = 'data/{}'.format(ticker)

    #get data using yfinance
    h.getTickerData(ticker)

    #Enter prediction
    predlist = ["GREEN", "RED", "FLAT"]
    while True:
        pred = "treen"#input("Enter your prediction, Green(+0.5+%)/Red(-0.5+%)/Flat")
        pred = pred.upper() #standarize the input to capital letters
        if pred in predlist:
            break
        else:
            print ("Invalid input, try again.")

        

    return 0

if main() == 1:
    print("Program exited with error.")
else:
    print("Progam executed successfully.")
