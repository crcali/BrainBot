import re
import time
import threading
import signal
import serial
import sig_mov
#opens the serial port over Bluetooth
#sp = serial.Serial('/dev/ttyACM0', 9600, timeout=0)

#opens the serial port through a USB-to-Serial cable
sp = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)

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

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        # ... Other thread setup code here ...

    def run(self):
        print('Thread #%s started' % self.ident)
        print("temp = ", self.command)
        def moveServo(servoNumber, position):
            if not self.shutdown_flag.is_set():
                sp.write(("#%i P%i T15\r" %(int(servoNumber), int(position))).encode())
                time.sleep(.25)
        def defaultPosition():
            # set the servos to the inital position
            sp.write("#0 P1425 #1 P1850 #2 P600 #8 P1500 #9 P1000 #10 P1500 \
                      #16 P1500 #17 P1600 #18 P1475 #24 P1600 #25 P2215 #26 P1450 T.5\r".encode())
        
        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            time.sleep(0.5)

            if self.command == "stop":
                defaultPosition()

            if self.command == 'forward':
                #commands to move forward with the parameters
                self.speed = int(self.speed)
                waitTime = (self.speed/100)-1

                if not self.shutdown_flag.is_set(): defaultPosition()
                
                #lifts up first leg and ensures the robot maintains proper balance
                if not self.shutdown_flag.is_set(): sp.write(("#2 P500 #8 P1950 T550\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1)
                moveServo(25, 1800)
                moveServo(24, 1400)
                if not self.shutdown_flag.is_set(): sp.write(("#25 P2215 #26 P1450 T250\r").encode())
                if not self.shutdown_flag.is_set(): sp.write(("#2 P600 #8 P1500 T250\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(.75)

                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

                #lifts up second leg 
                moveServo(1, 1675)
                moveServo(0, 1700)
                moveServo(1, 1850)    

                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

                #lifts up third leg and ensures the robot maintains proper balance            
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1550 #24 P1800 #10 P1690 T550\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1)
                moveServo(17, 1900)
                moveServo(16, 1150)
                moveServo(17, 1600)
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1950 #24 P1200 #10 P1500 T250\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(.75)
                
                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

                #lifts up forth leg 
                moveServo(9, 1400)
                moveServo(8, 1925)
                moveServo(9, 1000)


                if not self.shutdown_flag.is_set(): time.sleep(waitTime)       
            
                #moves body forward
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(.1)

            if self.command == 'backward':
                #commands to move backward with the parameters
                self.speed = int(self.speed)
                defaultPosition()
                waitTime = (int(self.speed)/1000)+.35
                
                #moves legs to balance robot
                if not self.shutdown_flag.is_set(): sp.write(("#8 P1750 #16 P1250 #2 P500 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1.75) 
                
                #lifts up first leg
                moveServo(25, 1600, self.speed, waitTime)
                moveServo(24, 2225, self.speed, waitTime)
                moveServo(25, 2215, self.speed, waitTime)
                
                #lifts up second leg 
                moveServo(17, 2500, self.speed, waitTime)
                moveServo(16, 1975, self.speed, waitTime)
                moveServo(17, 1600, self.speed, waitTime)
                
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1800 #18 P1700 #24 P1725 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1.75) 
                #lifts up third leg 
                moveServo(9, 1900, self.speed, waitTime)
                moveServo(8, 1225, self.speed, waitTime)
                moveServo(9, 1000, self.speed, waitTime)
                if not self.shutdown_flag.is_set(): sp.write(("#18 P1475 #24 P2225 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1.75) 
                
                #lifts up forth leg 
                moveServo(1, 1550, self.speed, waitTime)
                moveServo(0, 1075, self.speed, waitTime)
                moveServo(1, 1850, self.speed, waitTime)
                
                if not self.shutdown_flag.is_set(): time.sleep(2)       
            
                #moves body 
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 T400\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(2.5)
        
            if self.command == 'left':
                #commands to turn with the parameters
                self.speed = int(self.speed)
                waitTime = (int(self.speed/1000))+.25

                defaultPosition()
            
                #lifts up first leg to enable second leg to move
                if not self.shutdown_flag.is_set(): sp.write(("#24 P1540 #18 P1610 #0 P1690 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1.75)
                moveServo(9, 1890, self.speed, waitTime)
                moveServo(8, 1125, self.speed, waitTime)
                moveServo(9, 1000, self.speed, waitTime)
                if not self.shutdown_flag.is_set(): sp.write(("#24 P1600 #18 P1475 #0 P1425 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(waitTime + .5)

                #lifts up second leg 
                moveServo(1, 1350, self.speed, waitTime)
                moveServo(0, 1600, self.speed, waitTime)
                moveServo(1, 1850, self.speed, waitTime)

                #lifts up first leg 
                moveServo(9, 1890, self.speed, waitTime)
                moveServo(8, 1950, self.speed, waitTime)
                moveServo(9, 1000, self.speed, waitTime)

                #lifts up third leg 
                moveServo(25, 1600, self.speed, waitTime)
                moveServo(24, 2300, self.speed, waitTime)
                moveServo(25, 2215, self.speed, waitTime)

                #lifts up fourth leg 
                moveServo(17, 2250, self.speed, waitTime)
                moveServo(16, 2200, self.speed, waitTime)
                moveServo(17, 1600, self.speed, waitTime)


                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

                #moves body forward
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

            if self.command == 'right':
            #commands to turn with the parameters
                self.speed = int(self.speed)
                waitTime = (int(self.speed/1000))+.25

                defaultPosition()
            
                #lifts up fourth leg to enable second leg to move
                if not self.shutdown_flag.is_set(): sp.write(("#24 P1540 #18 P1610 #0 P1690 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(1.75)
                moveServo(9, 1890, self.speed, waitTime)
                moveServo(8, 1225, self.speed, waitTime)
                moveServo(9, 1000, self.speed, waitTime)
                if not self.shutdown_flag.is_set(): sp.write(("#24 P1600 #18 P1475 #0 P1425 T750\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(waitTime + .5)

                #lifts up first leg
                moveServo(1, 1350, self.speed, waitTime)
                moveServo(0, 1050, self.speed, waitTime)
                moveServo(1, 1850, self.speed, waitTime)

                #lifts up second leg 
                moveServo(17, 2250, self.speed, waitTime)
                moveServo(16, 800, self.speed, waitTime)
                moveServo(17, 1600, self.speed, waitTime)

                #lifts up third leg
                moveServo(25, 1600, self.speed, waitTime)
                moveServo(24, 900, self.speed, waitTime)
                moveServo(25, 2215, self.speed, waitTime)

                #lifts up fourth leg
                moveServo(9, 1890, self.speed, waitTime)
                moveServo(8, 900, self.speed, waitTime)
                moveServo(9, 1000, self.speed, waitTime)

                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

                #moves body forward
                if not self.shutdown_flag.is_set(): sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
                if not self.shutdown_flag.is_set(): time.sleep(waitTime)

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