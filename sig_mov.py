from __future__ import print_function
from IPython.display import HTML
import numpy as np
import pandas as pd
import peakutils as pku
import functools 
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
def movement_sequence(raw_data, bins_size, speed_rate, main_vector_method):
    '''
    Based on the binsize, divide the 'raw_data' into the individual bins by size 'bins_size', and
    
    Parameters:
        --raw_data:pandas dataframe(or 2 dimensional nd-array), the row repersents the time point , the column 
                    represents the electrodes(channels).
        
        --bins_size(int): the size of individual bin. decides the time interval for each bin.
        
        --speed_rate(float number >0 AND <1 ): change the speed manually and non-linearly, higher it is, faster speed you got
        
        -- main_vector_method: the method to reduce the 64 dimensions to 1 dimension
    Returns:
        --bins_list: the list of parameters speed and in each bin distance 
    
    '''
    flag = 0
    bins_list = []
    len_raw_data = len(raw_data)
    reduced_neurosig = np.array(main_vector_method(raw_data))
    peak_collection = signal_speed(reduced_neurosig,speed_rate,bins_size)
    while(flag < len_raw_data):
        speed_temp = 0
        for i in peak_collection:
            if i > flag+bins_size:
                break
            peak_collection = np.delete(peak_collection,0)
            speed_temp += 1

        bins_list.append(speed_temp)
        flag += bins_size
    
    return bins_list

def signal_movement(signal, speed_rate, bins_size):
    '''
    set the number of the peaks as the indicator of speed
    '''
    speed = pku.indexes(signal, speed_rate, bins_size/20)
    if speed%2 == 1:
        return 'forward {0}'.format(speed*10)
    else
        return 'backward {0}'.format(speed*10)

def signal_direction(signal):
    
    pass

class SignalAnimation(object):
    '''
    generate the necessary animation function.

    ---args---

       --ax(matplotlib.Axes object):
             the position of the graph
       --signal_array(1-d array): 
             signal data
       --title(string):
             the title of the graph
       --kwargs:
            'time_resolution':(unit:s) default: 0.001s. the time resolution using in the recording length
            'display_time_range':(unit:s) default: [-0.01,0.01], the time range shown in the animation 
            'xticks':default:[-0.01,0,0.01] the position of the xticks
            'xtick_label':default:['past','now','future'], the label of xticks
            'display_interval':default:200 determine the refreshing speed of the 
            'fragment': np.arange(0,10)}

    ---method----
       init:
          --args:
              the same as the args for the class
          --function:
              initialize the basic frame of the graph, set the kwargs variables shows above,and title
          --return:
              none


       __call__:
           --args：
               timing, denote the nth data point counting from the first one from the start of the fragment.
           --function:
               update the present frame
           --return:
                tuple within line object(matplotlib) :the signal curve at this time
       --init:
           --args:
               none
           --function:
               provide the first line or dot, since the line object has nothing, necessary but does nothing to the plot.
           --return:
               tuple within line object(matplotlib) with nothing in it.
    '''
    def __init__(self, ax, signal_array,title = 'angle', **kwargs):
        property_ani = {
                'time_resolution':0.001,
                'display_time_range':[-0.01,0.01],
                'xticks':[-0.01,0,0.01],
                'xtick_label':['past','now','future'],
                'display_interval':200,
                'fragment': np.arange(0,10)}
        variable_set = set(property_ani.keys())
        for key,value in kwargs.items():
            if key in variable_set:
                property_ani[key] = value
            else:
                raise('wrong keyword {0}'.format(key))
        self.__display_time_range = np.arange(property_ani['display_time_range'][0],
                                              property_ani['display_time_range'][1]+
                                              property_ani['time_resolution'],
                                              property_ani['time_resolution'])
        self.__display_length  = len(self.__display_time_range)
        self.__display_index_range = np.arange(0, self.__display_length)
        self.__xticks = list(np.ceil(np.divide(property_ani['xticks'],property_ani['time_resolution']))
                             +self.__display_length//2)
        # the middle point of the graph
        self.__ax = ax
        self.__ax.axvline(x= self.__display_length//2,color ='r')
        self.__line, = ax.plot([], [], 'b-')
        self.__ax.set_ylim([0, np.max(signal_array)])
        self.__ax.set_xlim([0,self.__display_length-1])
        self.__ax.set_title(title,loc = 'left')
        self.__ax.set_ylabel('Amplitude')
        self.__ax.set_xticks(list(self.__xticks))
        self.__ax.set_xticklabels(property_ani['xtick_label'])
        #two line below is to show make the signal look normal at the begining and the end
        self.__signal_array = np.append(-1*np.ones(self.__display_length//2+1,),signal_array)
        self.__signal_array = np.append(self.__signal_array, -1*np.ones(self.__display_length//2+1,))
    def init(self):
        #self.__timing = 0
        self.__line.set_data([], [])
        return self.__line,
    def __call__(self,timing):
        self.__line.set_data(self.__display_index_range, self.__signal_array[timing:timing+self.__display_length])
        return self.__line,
