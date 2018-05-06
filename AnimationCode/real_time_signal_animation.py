import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
from multiprocessing import *
import time
import os
import pickle
import numpy as np
import serial
import threading
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
collection = []
'''
General description:

RealTimSigAni class is to seperate the graph into 3 chunks. and take the chunk with the left red line between the two yellow lines
in the middle as the current chunk to calculate the speed.
and when it receives one data(float or int) it updates its graph

For rest of the code

Basically, you should establish two virtual series(in ubuntu I use $socat -d -d pty pty to generate it) called input one and output one and build connections between them.
Take the input one as a process, and output one as a another, send the neural data using pickle from input one to the output
one so that you could get the python subject.

'''


class RealTimeSigAni(object):

    def __init__(self, fig, ax, time_resolution, index_interval, ymax):
        '''
        Initializing a basic framework of this animation
        Parameters:
        -----------------------------------------------------
            --time_resolution: resolution of the data
            --index_interval: the interval for extracting information
        '''
        self.signal_array = []
        self.time_resolution = time_resolution
        self.window_range = ([0, 3 * index_interval])
        self.window_length = 3 * index_interval
        self.index_interval = index_interval
        self.fig = fig
        self.ax = ax
        self.speed = 0
        self.speed_change_flag = False
        # set the general graph of the signal window
        self.ax.set_xlim(self.window_range)
        self.ax.set_ylim([0, ymax])
        self.ax.invert_xaxis()
        # draw a red window for the processed information
        self.ax.axvline(index_interval, color='red')
        self.ax.axvline(2 * index_interval, color='red')
        # draw the signal curve to manifest the signal
        self.signal_curve, = ax.plot([], [], 'b-')
        self.ax.set_ylabel('firing amplitude')
        self.ax.set_xlabel('time')
        self.ax.set_xticks([index_interval, 2 * index_interval])
        self.speed_display = self.ax.text(0.9, 0.9, 'Speed:0', horizontalalignment='center', verticalalignment='center',
                                          transform=ax.transAxes)
        # use three yellow lines to distringuish different chunks
        self.line1 = self.ax.axvline(0, color='yellow')
        self.line2 = self.ax.axvline(0, color='yellow')
        self.line3 = self.ax.axvline(0, color='yellow')
        self.line_collection = []

    def __call__(self, data):
        # every time a data reaches, update the grpah by phase 1 or phase 2,because they got different
        self.signal_array.append(data)
        if len(self.signal_array) <= self.window_range[1]:
            return self.phase_1_plot()
        else:
            if len(self.signal_array) > 8 * self.index_interval:
                self.signal_array = self.signal_array[-(self.window_length + 5):]
                # here plus 5 is to avoid to fall in condition (2 lines above)
            return self.phase_2_plot()

    def phase_1_plot(self, speed_method=np.sum):
        # undone:change ylim
        length = len(self.signal_array)
        # print(self.signal_array)
        self.signal_curve.set_xdata(np.arange(1, 1 + length))
        self.signal_curve.set_ydata(self.signal_array[::-1])
        self.speed_change_flag = False
        if length == 1:
            self.line_collection.append(self.line1)

        if length == self.index_interval:
            self.speed = speed_method(
                self.signal_array[-self.index_interval:])
            self.speed_display._text = 'Speed {0}'.format(self.speed)
            self.speed_change_flag = True

        if length == self.index_interval + 1:
            self.line_collection.append(self.line2)

        if length == 2 * self.index_interval:
            self.speed = speed_method(
                self.signal_array[-self.index_interval:])
            self.speed_display._text = 'Speed {0}'.format(self.speed)
            self.speed_change_flag = True
        if length == 2 * self.index_interval + 1:
            self.line_collection.append(self.line3)

        for line in self.line_collection:
            line.set_xdata(line._x[1] + 1)
            self.ax.draw_artist(line)
        self.ax.draw_artist(self.signal_curve)
        self.ax.autoscale_view()
        self.fig.canvas.flush_events()
        return self.speed, self.speed_change_flag

    def phase_2_plot(self, speed_method=np.sum):
        self.speed_change_flag = False
        for line in self.line_collection:
            if line._x[1] == self.window_range[1]:
                line.set_xdata(1)
                self.speed = speed_method(self.signal_array[-self.index_interval:])
                self.speed_display._text = 'Speed {0}'.format(self.speed)
                self.ax.draw_artist(self.speed_display)
                self.ax.draw_artist(line)
                self.speed_change_flag = True
            else:
                line.set_xdata(line._x[1] + 1)
                self.ax.draw_artist(line)
        self.signal_curve.set_ydata((self.signal_array[-self.window_range[1]:])[::-1])
        self.ax.draw_artist(self.signal_curve)
        self.ax.autoscale_view()
        self.fig.canvas.flush_events()
        return self.speed, self.speed_change_flag


def Transmit(ser, neural_data, slow_ratio, recording_start=0, time_resolution=0.001):
    current_spiking = recording_start
    start_time = time.time()
    time_interval = time_resolution * slow_ratio
    while (True):
        pickle.dump(neural_data[current_spiking, :], ser)
        current_spiking += 1
        time.sleep(time_interval - ((time.time() - start_time) % time_interval))


def Output(ser, slow_ratio, time_resolution, index_interval, ymax):
    file_name = 'robot.txt'
    file_robot = open(file_name, 'w')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.ion()
    animation = RealTimeSigAni(fig, ax, 0.1, index_interval, ymax)
    fig.canvas.draw()
    fig.show()
    collection = []
    start_time = time.time()
    time_interval = slow_ratio * time_resolution
    while (True):
        spiking = pickle.load(ser)
        speed, speed_change_flag = animation(sum(spiking))
        # multiprocessing went wrong here, I think it's the problem of matplotlib and multiprocessing and threads faila on the multiprocessing modele.
        # animation_thread = Process(target=animation, args=(sum(spiking),))
        # animation_thread.start()
        if speed_change_flag:
            thread_robot = threading.Thread(target=file_robot.write, args=('the speed is {0}\n'.format(speed),))
            thread_robot.start()
        time.sleep(time_interval - ((time.time() - start_time) % time_interval))


if __name__ == '__main__':
    try:

        neural_data = pd.read_csv('dish_11_experiment_41.csv')
        neural_data = neural_data.as_matrix()

        time_resolution = 0.001
        index_interval = 100 # The datapoints in each chunk
        slow_ratio = 20  # the times that we animate our signals
        recording_start = 1000  # the correspondent time points that we choose to animate our dataset
        ymax = 700  # the max of the yaxis inploting
        ser_in = serial.Serial('/dev/pts/22', write_timeout=100)  # these two is the virtual series
        ser_out = serial.Serial('/dev/pts/23', baudrate=19200)

        pro_in = Process(target=Transmit, args=(ser_in, neural_data, slow_ratio, recording_start, time_resolution,))
        pro_out = Process(target=Output, args=(ser_out, slow_ratio, time_resolution, index_interval, ymax,))
        pro_in.start()
        pro_out.start()

    except KeyboardInterrupt:
        ser_in.close()
        ser_out.close()
        # file_handle.close()