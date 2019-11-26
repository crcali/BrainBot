# modules for robot
import re
import time
import threading
import signal
import serial
from RobotCode.finalQuadCode import *
from RobotCode.finalWheeledCode import *

# modules for brinstaain
#from IPython.display import HTML
import numpy as np
import pandas as pd
import peakutils as pku
import functools

#from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib import gridspec
from peakutils.sig_mov import *
import pickle

#open-ephys redesign
import pyopenephys
import os
import scipy.signal
import scipy.io
import time
import struct
from copy import deepcopy

# constants
NUM_HEADER_BYTES = 1024
SAMPLES_PER_RECORD = 1024
BYTES_PER_SAMPLE = 2
RECORD_SIZE = 4 + 8 + SAMPLES_PER_RECORD * BYTES_PER_SAMPLE + 10 # size of each continuous record in bytes

def readHeader(f):
    header = { }
    h = f.read(1024).decode().replace('\n','').replace('header.','')
    for i,item in enumerate(h.split(';')):
        if '=' in item:
            header[item.split(' = ')[0]] = item.split(' = ')[1]
    return header

def downsample(trace,down):
    downsampled = scipy.signal.resample(trace,np.shape(trace)[0]/down)
    return downsampled

def loadContinuous(filepath, dtype = float):

    assert dtype in (float, np.int16), \
      'Invalid data type specified for loadContinous, valid types are float and np.int16'

    print("Loading continuous data...")

    ch = { }

    #read in the data
    f = open(filepath,'rb')

    fileLength = os.fstat(f.fileno()).st_size

    # calculate number of samples
    recordBytes = fileLength - NUM_HEADER_BYTES
    #if  recordBytes % RECORD_SIZE != 0:
        #raise Exception("File size is not consistent with a continuous file: may be corrupt")
    nrec = recordBytes // RECORD_SIZE
    nsamp = nrec * SAMPLES_PER_RECORD
    # pre-allocate samples
    samples = np.zeros(nsamp, dtype)
    timestamps = np.zeros(nrec)
    recordingNumbers = np.zeros(nrec)
    indices = np.arange(0, nsamp + 1, SAMPLES_PER_RECORD, np.dtype(np.int64))

    header = readHeader(f)

    recIndices = np.arange(0, nrec)

    for recordNumber in recIndices:

        timestamps[recordNumber] = np.fromfile(f,np.dtype('<i8'),1) # little-endian 64-bit signed integer
        N = np.fromfile(f,np.dtype('<u2'),1)[0] # little-endian 16-bit unsigned integer

        #print index

        if N != SAMPLES_PER_RECORD:
            raise Exception('Found corrupted record in block ' + str(recordNumber))

        recordingNumbers[recordNumber] = (np.fromfile(f,np.dtype('>u2'),1)) # big-endian 16-bit unsigned integer

        if dtype == float: # Convert data to float array and convert bits to voltage.
            data = np.fromfile(f,np.dtype('>i2'),N) * float(header['bitVolts']) # big-endian 16-bit signed integer, multiplied by bitVolts
        else:  # Keep data in signed 16 bit integer format.
            data = np.fromfile(f,np.dtype('>i2'),N)  # big-endian 16-bit signed integer
        samples[indices[recordNumber]:indices[recordNumber+1]] = data

        marker = f.read(10) # dump

    #print recordNumber
    #print index

    ch['header'] = header
    ch['timestamps'] = timestamps
    ch['data'] = samples  # OR use downsample(samples,1), to save space
    ch['recordingNumber'] = recordingNumbers
    f.close()
    return ch

# stimulation setup

## stim = serial.Serial('## path to stimjim ##', 112500, timeout=0)
initCommand = "S0,0,1,2000,1000000;"
## stim.write(initCommand)

voltage = 100; # voltage in mV
current = 100; # current in uA
duration = 150; # duration of the pulse train in microseconds

# load and preprocess neural data
file = loadContinuous("/Users/christophercaligiuri/Documents/open-ephys/2019-10-27_13-06-05/100_CH0.continuous") 

neurosignal = file['data']

# parameter definition
have_robot = True
robot = 'wheeled'
LOOP_TIME = 0.5 # seconds
RUN_TIME = 30 # seconds
NUM_LOOPS = RUN_TIME/LOOP_TIME

FS = 1000.
neural_index_interval = int(LOOP_TIME*FS)
speed_rate = 0.01
MAX_SPEED = 900
MIN_SPEED = 0
INVERT_SPEED = 2200
sig_max = np.max(neurosignal)


# initialize plot
fig = plt.figure(figsize=(16,4))
gs = gridspec.GridSpec(1, 2, width_ratios=[5, 1])

# display neural data
ax1 = plt.subplot(gs[0])
line1, = ax1.plot(np.arange(neural_index_interval), np.ones(neural_index_interval), 'r-') # Returns a tuple of line objects, thus the comma
plt.ylim((0,sig_max))
plt.ylabel('Neural Firing')

# display robot speed
ax2 = plt.subplot(gs[1])
line2, = ax2.bar(0, 0, width=0.2) # Returns a tuple of line objects, thus the comma
plt.ylabel('Robot Speed')
plt.xlim([-0.5, 0.5])
plt.ylim((0,1))
#plt.show()


#### main loop
# Register the signal handlers if robot is connected
if have_robot:
    # open serial port
    if (robot == 'quadruepd'): sp = serial.Serial('/dev/cu.usbmodem1451201', 38400, timeout=0)
    if (robot == 'wheeled'): sp = serial.Serial('/dev/cu.usbserial-145120', 115200, timeout=0)
    #signal.signal(signal.SIGTERM, service_shutdown)
    #signal.signal(signal.SIGINT, service_shutdown)

print('Starting the Main Program')

# Start the job threads
# Keep the main thread running, otherwise signals are ignored.
running = True
loop_counter = 0
curr_neural_index = 0
while running is True:
    # PAUSE LOOP
    time.sleep(LOOP_TIME)
    loop_counter += 1

    #print(cmd_directions)
    #print(running)

    # USER KEYBOARD INPUT
    # command=raw_input("::>")

    # NEURAL DATA PROCESSING ----

    ## inside loop
    curr_brain_signal = neurosignal[curr_neural_index:curr_neural_index+neural_index_interval]
    curr_neural_index = curr_neural_index + neural_index_interval

    ### old transform
    # movement = signal_movement(curr_brain_signal,speed_rate,neural_index_interval)
    # movement = (2000-(100*movement))/5

    # fr_to_speed returns a float between 0 to 1, scaled to absolute max
    movement = fr_to_speed(curr_brain_signal, sig_max)

    # need to invert speed because small number is faster
    invertedMovement = INVERT_SPEED - (fr_to_speed(curr_brain_signal, sig_max)*(MAX_SPEED-MIN_SPEED)+MIN_SPEED)

    move_time = 5.0
    CMD_direction = 'forward'
    CMD_speed = invertedMovement
    # ---------------------------

    print(curr_neural_index, movement)

    # VISUALIZATION
    line1.set_ydata(curr_brain_signal)
    line2.set_height(movement)

    ax1.set_xlabel('Time (ms)')

    # fig.canvas.draw()
    # fig.canvas.flush_events()
    plt.draw()
    plt.pause(1e-17)
    time.sleep(0.1)

    # COMMUNICATION TO ROBOT
    if have_robot:
        try:
            activethread.shutdown_flag.set()
            activethread.join()
        except:
            print("No running threads")

        # Terminate thread if exit command is received, or reached loop number
        if CMD_direction == 'exit' or loop_counter > NUM_LOOPS:
            # Terminate the running threads.
            # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
            activethread.shutdown_flag.set()
            # Wait for the threads to close...
            activethread.join()
            running=False
        else:
            # send command
            print('Sending command')
            if robot == 'quadruped':
                activethread=QuadCommands(CMD_direction, CMD_speed, robot, stim, voltage, current, duration)
                activethread.start()
            elif robot == 'wheeled':
                activethread=WheeledCommands(CMD_direction, CMD_speed, robot, stim, voltage, current, duration)
                activethread.start()
            time.sleep(move_time)


print('Exiting main program')

#close serial port
sp.close()
isClosed = sp.is_open
while isClosed == True:
    sp.close
    isClosed = sp.is_open
