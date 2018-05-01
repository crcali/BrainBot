
# modules for robot
import re
import time
import threading
import signal
import serial
from BrainBotTestCode import *

# modules for brinstaain
#from IPython.display import HTML
import numpy as np
import pandas as pd
import peakutils as pku
import functools
#from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from sig_mov import *
import pickle
#######

# load and preprocess neural data
braindata_file = './data/dish_5_experiment_37_100000-110000ms.obj'
with open(braindata_file,'rb') as f:
    neurosignal = pickle.load(f, encoding='ASCII')

vector_method = functools.partial(np.sum,axis=1)
neurosignal = np.array(neurosignal.sum(axis = 1))

# parameter definition
LOOP_TIME = 0.5 # seconds
RUN_TIME = 30 # seconds
NUM_LOOPS = RUN_TIME/LOOP_TIME

FS = 1000.
neural_index_interval = int(LOOP_TIME*FS)
speed_rate = 0.01

# open serial port
sp = serial.Serial('/dev/ttyACM0', 11520, timeout=0)


# initialize plot
fig = plt.figure(figsize=(16,8))
# display neural data
ax1 = fig.add_subplot(211)
line1, = ax1.plot(np.arange(neural_index_interval), np.ones(neural_index_interval), 'r-') # Returns a tuple of line objects, thus the comma
plt.ylim((0,np.max(neurosignal)))
plt.ylabel('Neural Firing')
# display command
ax2 = fig.add_subplot(212)
line2, = ax2.plot(np.arange(neural_index_interval), np.ones(neural_index_interval), 'r-') # Returns a tuple of line objects, thus the comma
plt.ylabel('Robot Speed')
plt.ylim((0,800))
#plt.show()

have_robot = True
# main loop

# Register the signal handlers
if have_robot:
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

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
    movement = signal_movement(curr_brain_signal,speed_rate,neural_index_interval)
    curr_neural_index = curr_neural_index + neural_index_interval

    movement = (2000-(100*movement))/5
    move_time = 10.0
    CMD_direction = 'forward'
    CMD_speed = movement
    # ---------------------------

    print(curr_neural_index, movement)

    # VISUALIZATION
    line1.set_ydata(curr_brain_signal)
    line2.set_ydata(movement)
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