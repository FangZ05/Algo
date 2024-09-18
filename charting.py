#scientific libraries
import numpy as np
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.pyplot as plt

def zoom_factory(ax,base_scale = 2.):
    def zoom_fun(event):
        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5

        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print (event.button)
        # set new limits
        ax.set_xlim([xdata - cur_xrange*scale_factor,
                     xdata + cur_xrange*scale_factor])
        ax.set_ylim([ydata - cur_yrange*scale_factor,
                     ydata + cur_yrange*scale_factor])
        plt.draw() # force re-draw

    fig = ax.get_figure() # get the figure of interest
    
    # attach the call back
    fig.canvas.mpl_connect('scroll_event',zoom_fun)

    #return the function
    return zoom_fun


#OHLC candlestick chart
def candlestickPlot(ticker, pricedf, width = 0.4, volprof = True):
    size = len(pricedf)
    x = np.arange(0,size)
    fig, axs = plt.subplots(1, figsize=(12,6))
    for idx, val in pricedf.iterrows(): #iterate per row
        #define colour
        color = 'black'
        if val['Open'] > val['Close']: 
            color= 'red'
            height = val['Open'] - val['Close']
        elif val['Open'] < val['Close']: 
            color= 'green'
            height = val['Close'] - val['Open']
        else:
            height = 0

        # high/low line
        axs.plot([x[idx], x[idx]], 
                 [val['Low'], val['High']], 
                 color=color)
        #open/close bar
        axs.bar(x[idx], 
                height,
                width, 
                bottom = val['Close'],
                color=color)
    
    #formate the graph
    axs.set_xticks(x[::1], pricedf['Time'][::1], rotation = 90, fontsize = 6) #xtick
    axs.xaxis.set_major_locator(MultipleLocator(int(size/20))) #xtick spacing
    axs.grid(alpha=0.5) #grid
    axs.set_title('{}'.format(ticker)) #title
    
    #return the axis for further graphing
    return axs