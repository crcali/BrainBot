import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
import time


class RealTimeSigAni(object):

    def __init__(self, ax, time_resolution,index_interval):
        '''
        Initializing a basic framework of this animation
        Parameters:
        -----------------------------------------------------
            --time_resolution: resolution of the data
            --index_interval: the interval for extracting information
        '''
        self.signal_array=[]
        self.time_resolution = time_resolution
        self.window_range = ([0, 3*index_interval])
        self.window_length = 3*index_interval
        self.index_interval = index_interval
        self.ax = ax
        self.background = fig.canvas.copy_from_bbox(ax.bbox)
        self.speed = 0
        # set the general graph of the signal window
        self.ax.set_xlim(self.window_range)
        self.ax.set_ylim([-10,10])
        self.ax.invert_xaxis()
        # draw a red window for the processed information
        self.ax.axvline(index_interval, color='red')
        self.ax.axvline(2*index_interval, color='red')
        self.signal_curve, = ax.plot([], [], 'r-')
        self.ax.set_ylabel('firing amplitude')
        self.ax.set_xlabel('time')
        self.ax.set_xticks([index_interval,2*index_interval])
        self.speed_display = self.ax.text(0.9, 0.9, 'Speed:0', horizontalalignment='center', verticalalignment='center',  transform=ax.transAxes)
        self.line1 = self.ax.axvline(0, color='yellow')
        self.line2 = self.ax.axvline(0, color='yellow')
        self.line3 = self.ax.axvline(0, color='yellow')
        self.line_collection = []


    def __call__(self, data):
        self.signal_array.append(data)
        if len(self.signal_array) <= self.window_range[1]:
            self.phase_1_plot()
        else:
            if len(self.signal_array)>8*self.index_interval:
                self.signal_array = self.signal_array[-(self.window_length+5):]
                # here plus 5 is to avoid to fall in condition (2 lines above)
            self.phase_2_plot()


    def phase_1_plot(self,speed_method=np.sum):
        # undone:change ylim
        length = len(self.signal_array)
        self.signal_curve.set_xdata(np.arange(1, 1+length))
        self.signal_curve.set_ydata(self.signal_array)

        if length == 1:
            self.line_collection.append(self.line1)

        if length == self.index_interval:
            self.speed = speed_method(
                    self.signal_array[-self.index_interval:])
            self.speed_display._text = 'Speed {0}'.format(self.speed)

        if length==self.index_interval+1:
            self.line_collection.append(self.line2)

        if length==2*self.index_interval:
            self.speed = speed_method(
                    self.signal_array[-self.index_interval:])
            self.speed_display._text = 'Speed {0}'.format(self.speed)

        if length==2*self.index_interval+1:
            self.line_collection.append(self.line3)

        for line in self.line_collection:
            line.set_xdata(line._x[1]+1)
            self.ax.draw_artist(line)
        self.ax.draw_artist(self.signal_curve)

    def phase_2_plot(self,speed_method = np.sum):
        for line in self.line_collection:
            if line._x[1]==self.window_range[1]:
                line.set_xdata(1)
                self.speed = speed_method(self.signal_array[-self.index_interval:])
                self.speed_display._text = 'Speed {0}'.format(self.speed)
                self.ax.draw_artist(self.speed_display)
                self.ax.draw_artist(line)
            else:
                line.set_xdata(line._x[1]+1)
                self.ax.draw_artist(line)
        self.signal_curve.set_ydata((self.signal_array[-self.window_range[1]:])[::-1])
        self.ax.draw_artist(self.signal_curve)
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
plt.ion()
time_resolution = 0.001
index_interval = 10

test=RealTimeSigAni(ax,time_resolution,index_interval)
fig.canvas.draw()
fig.show()
number = np.random.randn(100)
for i in number:
    test(i)
    fig.canvas.flush_events()
    time.sleep(0.3)