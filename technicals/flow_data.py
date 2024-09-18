"""
Technical Inducator: daily Volume Delta

Estimates the buy vs. sell volume

input: ticker
    grabs pricedf, and pricedf at lower timeframe

function: using the change price on lower timeframe as a proxy for buy or sell. 
    Then calculates the difference in volume between buy and sell candle.

output: volume delta
    the net buy minus sell volume


"""
"""
Pine Script

indicator("Volume Delta", format=format.volume)

lowerTimeframeTooltip = "The indicator scans lower timeframe data to approximate up and down volume used in the delta calculation. By default, the timeframe is chosen automatically. These inputs override this with a custom timeframe.
 \n\nHigher timeframes provide more historical data, but the data will be less precise."
useCustomTimeframeInput = input.bool(false, "Use custom timeframe", tooltip = lowerTimeframeTooltip)
lowerTimeframeInput = input.timeframe("1", "Timeframe")

upAndDownVolume() =>
    posVol = 0.0
    negVol = 0.0
    
    var isBuyVolume = true    

    switch
        close > open     => isBuyVolume := true
        close < open     => isBuyVolume := false
        close > close[1] => isBuyVolume := true
        close < close[1] => isBuyVolume := false

    if isBuyVolume
        posVol += volume
    else
        negVol -= volume

    posVol + negVol

var lowerTimeframe = switch
    useCustomTimeframeInput => lowerTimeframeInput
    timeframe.isseconds     => "1S"
    timeframe.isintraday    => "1"
    timeframe.isdaily       => "5"
    => "60"

diffVolArray = request.security_lower_tf(syminfo.tickerid, lowerTimeframe, upAndDownVolume())

getHighLow(arr) =>
    float cumVolume = na
    float maxVolume = na
    float minVolume = na

    for item in arr
        cumVolume := nz(cumVolume) + item
        maxVolume := math.max(nz(maxVolume), cumVolume)
        minVolume := math.min(nz(minVolume), cumVolume)

    [maxVolume, minVolume, cumVolume]

[maxVolume, minVolume, lastVolume] = getHighLow(diffVolArray)
openVolume = not na(lastVolume) ? 0.0 : na
col = lastVolume > 0 ? color.teal : color.red
hline(0)
plotcandle(openVolume, maxVolume, minVolume, lastVolume, "Volume Delta", color = col, bordercolor = col, wickcolor = col)

var cumVol = 0.
cumVol += nz(volume)
if barstate.islast and cumVol == 0
    runtime.error("The data vendor doesn't provide volume data for this symbol.")

"""
import yfinData as ydata
def volume_delta(ticker, update=True):
    #get the higher & lower price data
    pricedfLower = ydata.stock_data_get(ticker, '1m', update=update, chrono=True)
    pricedfHigher = ydata.stock_data_get(ticker, '1d', update=update, chrono=True)


    #limit the domain to that of the lower timeframe since it should have less data
    start = pricedfLower['Time'].iloc[0]
    end = pricedfLower['Time'].iloc[-1]

    analyseddf = pricedfHigher[((pricedfHigher['Time'] > start ) & (pricedfHigher['Time'] < end))]