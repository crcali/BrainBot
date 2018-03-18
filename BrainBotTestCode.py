import serial
import time

#open a serial port
serial.Serial('/dev/ttyUSB0').close()
sp = serial.Serial('/dev/ttyUSB0', 9600)

# set the servos to the inital position
sp.write("#0 P1425\r".encode())
sp.write("#1 P2150\r".encode())
sp.write("#2 P1625\r".encode())
sp.write("#8 P1500\r".encode())
sp.write("#9 P2300\r".encode())
sp.write("#10 P1500\r".encode())
sp.write("#16 P1500\r".encode())
sp.write("#17 P1600\r".encode())
sp.write("#18 P1475\r".encode())
sp.write("#24 P1600\r".encode())
sp.write("#25 P2215\r".encode())
sp.write("#26 P1450\r".encode())

#sets up the move forward module 
def moveForward(speed, distance):
	#commands to move forward with the parameters
	numberOfTimes = (distance/5)*2


	for x in range (0,numberOfTimes):
		#lifts up first leg 
		sp.write(("#25 P1600 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#24 P1200 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#25 P2215 T%s\r" %speed).encode())
		
		time.sleep(.5)

		#lifts up second leg 
		sp.write(("#1 P1535 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#0 P1950 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#1 P2150 T%i\r" %speed).encode())

		time.sleep(.5)

		#lifts up third leg 
		sp.write(("#17 P2500 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#16 P1000 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#17 P1600 T%i\r" %speed).encode())
		time.sleep(.5)

		time.sleep(.5)

		#lifts up forth leg 
		sp.write(("#9 P1600 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#8 P1900 T%i\r" %speed).encode())
		time.sleep(.5)
		sp.write(("#9 P2250 T%i\r" %speed).encode())
		time.sleep(.5)

		time.sleep(.5)

		#moves body forward
		sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())

		time.sleep(2)

def moveBackward(speed, distance):
	#commands to move backward with the parameters
	print "moveBackward"

def defultPosition():
	sp.write("#0 P1425 #1 P2150 #2 P1625 #8 P1500 #9 P2300 #10 P1500 #16 P1500 #17 P1600 #18 P1475 #24 P1600 #25 P2215 #26 P1450 T.5\r".encode())

#runs all the modules and gets user input
while True: 
	defultPosition()
	command = raw_input("Enter moveForward, moveBackward, or cancel: ")
	defultPosition()
	if command == "cancel":
		break 
	speedInput = input("Please enter the desired speed: ")
	distanceInput = input("Please enter the number of inches you wish the robot to move (must be a factor of 5): ")

	print ("Inputed Command: %s \n" % command)

	if command == "moveForward":
	#run the moveforward module

		print "initiating command\n"

		moveForward(speedInput, distanceInput)

		print "finsihed command; restarting and waiting for another input \n"
		
#close serial port
sp.close()