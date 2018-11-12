
# modules for robot
import re
import time
import threading
import signal
import serial
from RobotCode.finalRobotCode import *

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
#######

# load and preprocess neural data
braindata_file = './data/dish_5_experiment_37_100000-110000ms.obj'
with open(braindata_file,'rb') as f:
    neurosignal = pickle.load(f, encoding='ASCII')

vector_method = functools.partial(np.sum,axis=1)
neurosignal = np.array(neurosignal.sum(axis = 1))

# parameter definition
have_robot = True
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

# display command
ax2 = plt.subplot(gs[1])
line2, = ax2.bar(0, 0, width=0.2) # Returns a tuple of line objects, thus the comma
plt.ylabel('Robot Speed')
plt.xlim([-0.5, 0.5])
plt.ylim((0,INVERT_SPEED-MIN_SPEED))
#plt.show()


#### main loop
# Register the signal handlers if robot is connected
if have_robot:
    # open serial port
    sp = serial.Serial('/dev/ttyACM0', 11520, timeout=0)
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

#    print(cmd_directions)
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

    # May 4 update
    # fr_to_speed returns a float between 0 to 1, scaled to absolute max
    movement = fr_to_speed(curr_brain_signal, sig_max)
    # need to invert speed because small number is faster
    movement = INVERT_SPEED - (movement*(MAX_SPEED-MIN_SPEED)+MIN_SPEED)

    move_time = 10.0
    CMD_direction = 'forward'
    CMD_speed = movement
    # ---------------------------

    print(curr_neural_index, movement)

    # VISUALIZATION
    line1.set_ydata(curr_brain_signal)
    line2.set_height(movement)
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
            activethread=RobotCommands(CMD_direction, CMD_speed)
            activethread.start()
            time.sleep(move_time)


print('Exiting main program')

#close serial port
sp.close()
isClosed = sp.is_open
while isClosed == True:
    sp.close
    isClosed = sp.is_open
