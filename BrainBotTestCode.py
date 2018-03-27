import serial
import time

#open a serial port
sp = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)

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

#sets up the move backward module
def moveBackward(speed, distance):
	#commands to move backward with the parameters
	numberOfTimes = distance

	#!!run for x in range command when distance is refined!! 
	#lifts up first leg 
	sp.write(("#25 P1600 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#24 P2200 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#25 P2215 T%s\r" %speed).encode())
	
	time.sleep(.5)

	#lifts up second leg 
	sp.write(("#1 P1535 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#0 P1000 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#1 P2150 T%i\r" %speed).encode())

	time.sleep(.5)

	#lifts up third leg 
	sp.write(("#17 P2500 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#16 P1900 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#17 P1600 T%i\r" %speed).encode())
	time.sleep(.5)

	time.sleep(.5)

	#lifts up forth leg 
	sp.write(("#9 P1600 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#8 P900 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#9 P2250 T%i\r" %speed).encode())
	time.sleep(.5)

	time.sleep(.5)

	#moves body 
	sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())

	time.sleep(2)

#sets up the move backward module
def turn(speed, degrees):
	#commands to move backward with the parameters
	numberOfTimes = degrees

	#!!run for x in range command when distance is refined!! 
	#lifts up first leg 
	sp.write(("#25 P1600 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#24 P2200 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#25 P2215 T%s\r" %speed).encode())
	
	time.sleep(.5)

	#lifts up second leg 
	sp.write(("#1 P1535 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#0 P1000 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#1 P2150 T%i\r" %speed).encode())

	time.sleep(.5)

	#lifts up third leg 
	sp.write(("#17 P2500 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#16 P1900 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#17 P1600 T%i\r" %speed).encode())
	time.sleep(.5)

	time.sleep(.5)

	#lifts up forth leg 
	sp.write(("#9 P1600 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#8 P900 T%i\r" %speed).encode())
	time.sleep(.5)
	sp.write(("#9 P2250 T%i\r" %speed).encode())
	time.sleep(.5)

	time.sleep(.5)

	#moves body 
	sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())

	time.sleep(2)

#the defult, rest position 
def defultPosition():

	# set the servos to the inital position
	sp.write("#0 P1425 #1 P2150 #2 P1625 #8 P1500 #9 P2300 #10 P1500 #16 P1500 #17 P1600 #18 P1475 #24 P1600 #25 P2215 #26 P1450 T.5\r".encode())

#runs all the modules and gets user input
while True: 
	defultPosition()
	command = raw_input("Enter move forward, move backward, turn or cancel: ")
	defultPosition()
	if command == "cancel":
		break 
	if command == ("move forward") or (command == "move backward"):
		speedInput = input("Enter the desired speed: ")
		distanceInput = input("Enter the number of inches you wish the robot to move (must be a factor of 5): ")
	if command == "turn":
		speedInput = input("Enter the desired speed: ")
		degrees = input("Enter the number of degrees for the robot to move: ")

	print ("\nINPUTED COMMAND: %s \n" % command)

	if command == "move forward":
		#run the moveForward module

		print "Initiating command\n"

		moveForward(speedInput, distanceInput)

		print "Finsihed command; restarting and waiting for another input \n"

	if command == "move backward":
		#run the moveBackward module

		print "Initiating command\n"

		moveBackward(speedInput, distanceInput)

		print "Finished command; restarting and waiting for another input \n"

	if command == "turn":
		#runs the turn module

		print "Initiating command\n"

		turn(speedInput, degrees)

		print "Finished command; restarting and waiting for another input \n" 
		
#close serial port
sp.close()
isClosed = sp.is_open
while isClosed == True:
	sp.close
	isClosed = sp.is_open
	print isClosed