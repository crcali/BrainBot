import re
import time
import threading
import signal
import serial
import peakutils.sig_mov
#opens the serial port over Bluetooth
sp = serial.Serial('/dev/cu.usbmodem14401', 38400, timeout=0)

#opens the serial port through a USB-to-Serial cable
#sp = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)

# Directions = '''
# Enter your command in the following format: <forward | backward|left|right|stop> <speed (must be between 100 and 2000) (speed is not required if 'stop' is entered)>
# It will automatically run your entered command after ENTER is pressed
# Enter exit to close serial port and end program
# '''

class RobotCommands(threading.Thread):
    def __init__(self, INPUT, SPEED):
        threading.Thread.__init__(self)
        self.command = INPUT
        self.speed = SPEED
        self.calcSpeed = SPEED // 500
        int(self.calcSpeed)

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        # ... Other thread setup code here ...
        sp.write(str.encode('yyy'))
    def run(self):
        print('Thread #%s started' % self.ident)
        print("temp = ", self.command)
        def defaultPosition():
            # set the servos to the neutral position
            sp.write(str.encode('q'))

        if self.command == 'stop':
            if not self.shutdown_flag.is_set(): sp.write(str.encode('s'))

        if self.command == 'forward':
        #commands to move forward with the parameters
            if not self.shutdown_flag.is_set(): sp.write(str.encode('f'))
            if not self.shutdown_flag.is_set(): sp.write(str.encode('%i' % self.calcSpeed))

            read1 = sp.read()
            while (self.shutdown_flag.is_set() == False):
                if sp.read() != read1:
                    f = open("Ultrasonic_Values.txt","w+")
                    tdata = sp.read()           
                    time.sleep(1)              
                    data_left = sp.inWaiting()  # Get the number of characters ready to be read
                    tdata += sp.read(data_left) # Do the read and combine it with the first character
                    print(tdata)
                    f.write("%s" %tdata)
                    f.close()    


        if self.command == 'left':
        #commands to move left with the parameters
            if not self.shutdown_flag.is_set(): sp.write(str.encode('l'))
            if not self.shutdown_flag.is_set(): sp.write(str.encode('%i' % self.calcSpeed))
       
        if self.command == 'backward':
        #commands to move backward with the parameters
            if not self.shutdown_flag.is_set(): sp.write(str.encode('b'))
            if not self.shutdown_flag.is_set(): sp.write(str.encode('%i' % self.calcSpeed))

        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit


def main():
    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    print('Starting the Main Program')

    # Start the job threads
    # Keep the main thread running, otherwise signals are ignored.
    running = True
    while running is True:
        print(Directions)
        print(running)
        command=raw_input("::>")
        time.sleep(0.5)
        try:
            activethread.shutdown_flag.set()
            activethread.join()
        except:
            print("No running threads")
        if command == 'exit':
            # Terminate the running threads.
            # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
            activethread.shutdown_flag.set()
            # Wait for the threads to close...
            activethread.join()
            running=False
        else:
            raw=re.split(" ", command)
            if len(raw) == 2 and (raw[0] == "forward" or raw[0] == "backward"):
                if ((int(raw[1]) > 100 and int(raw[1]) < 2000)):
                    command=raw[0]
                    speed=raw[1]
                    activethread=RobotCommands(command, speed)
                    activethread.start()
                else:
                    print("Incorrect Format: <forward|backward> <speed>")
            elif len(raw) == 2 and ((raw[0] == "right") or (raw[0] == "left")):
                if (int(raw[1]) > 100 and int(raw[1]) < 2000):
                    command=raw[0]
                    speed=raw[1]
                    activethread=RobotCommands(command, speed)
                    activethread.start()
                else:
                    print("Incorrect Format: <right|left> <speed>")
            elif (len(raw) == 1 and (raw[0] == "stop")):
                command=raw[0]
                speed=0
                activethread=RobotCommands(command, speed)
                activethread.start()
            else:
                print("Invalid Length, should be: <forward|backward|right|left|stop> <speed>")

    print('Exiting main program')

if __name__ == '__main__':
    main()
