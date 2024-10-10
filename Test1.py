import matplotlib.pyplot as plt

# Generate some data to plot
x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]

# Create a figure and a subplot
fig, ax = plt.subplots()

# Plot the data
ax.plot(x, y)

# Set the initial plot limits
xmin, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()

# Function to adjust the plot limits on scroll
def zoom(event):
    # Get the current x and y limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # Check if the scroll direction is forward or backward
    if event.button == 'up':
        # Zoom in by 10%
        xlim = (xlim[0] * 1.1, xlim[1] * 1.1)
        ylim = (ylim[0] * 1.1, ylim[1] * 1.1)
    elif event.button == 'down':
        # Zoom out by 10%
        xlim = (xlim[0] / 1.1, xlim[1] / 1.1)
        ylim = (ylim[0] / 1.1, ylim[1] / 1.1)
    
    # Set the new x and y limits
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # Redraw the plot
    fig.canvas.draw_idle()

# Connect the scroll event to the zoom function
fig.canvas.mpl_connect('scroll_event', zoom)

# Show the plot
plt.show()
