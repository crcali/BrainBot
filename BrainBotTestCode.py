import serial
import time

#open a serial port
sp = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)

def moveServo(servoNumber, position, speed, waitTime):
	sp.write(("#%i P%i T%i\r" %(servoNumber, position, speed)).encode())
	time.sleep(waitTime)

#sets up the move forward module 
def moveForward(speed, distance):
	#commands to move forward with the parameters
	numberOfTimes = (distance/5)*2

	waitTime = (speed/1000)+.25

	for x in range (0,numberOfTimes):
		#lifts up first leg 
		moveServo(25, 1600, speed, waitTime)
		moveServo(24, 1200, speed, waitTime)
		sp.write(("#25 P2215 #26 P1450 T%i\r" %speed).encode())
		time.sleep(waitTime)

		#lifts up second leg 
		moveServo(1, 1535, speed, waitTime)
		moveServo(0, 1950, speed, waitTime)
		moveServo(1, 2150, speed, waitTime)

		#lifts up third leg 
		moveServo(17, 2500, speed, waitTime)
		moveServo(16, 1000, speed, waitTime)
		moveServo(17, 1600, speed, waitTime)

		#lifts up forth leg 
		moveServo(9, 1600, speed, waitTime)
		moveServo(8, 1900, speed, waitTime)
		moveServo(9, 2250, speed, waitTime)

		#moves body forward
		sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
		time.sleep(waitTime)

#sets up the turn module
def moveBackward(speed, distance):
	#commands to turn with the parameters
	numberOfTimes = distance

	waitTime = (speed/1000)+.25

	#!!run for x in range command when distance is refined!! 
	#lifts up first leg 
	moveServo(25, 1600, speed, waitTime)
	moveServo(24, 2200, speed, waitTime)
	sp.write(("#25 P2215 #26 P1450 T%i\r" %speed).encode())
	time.sleep(waitTime)

	#lifts up second leg 
	moveServo(1, 1535, speed, waitTime)
	moveServo(0, 950, speed, waitTime)
	moveServo(1, 2150, speed, waitTime)

	#lifts up third leg 
	moveServo(17, 2250, speed, waitTime)
	moveServo(16, 1900, speed, waitTime)
	moveServo(17, 1600, speed, waitTime)

	#lifts up forth leg 
	moveServo(9, 1600, speed, waitTime)
	moveServo(8, 900, speed, waitTime)
	moveServo(9, 2250, speed, waitTime)

	#moves body 
	sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
	time.sleep(waitTime)

#sets up the move backward module
def turnCounterClockwise(speed, degrees):
	#commands to move backward with the parameters
	numberOfTimes = degrees/45

	waitTime = (speed/1000)+.25

	for x in range (0,numberOfTimes):
		#lifts up first leg 
		moveServo(25, 1600, speed, waitTime)
		moveServo(24, 2700, speed, waitTime)
		sp.write(("#25 P2215 #26 P1450 T%i\r" %speed).encode())
		time.sleep(waitTime)

		#lifts up second leg 
		moveServo(1, 1535, speed, waitTime)
		moveServo(0, 2300, speed, waitTime)
		moveServo(1, 2150, speed, waitTime)

		#lifts up third leg 
		moveServo(17, 2500, speed, waitTime)
		moveServo(16, 2300, speed, waitTime)
		moveServo(17, 1600, speed, waitTime)

		#lifts up forth leg 
		moveServo(9, 1600, speed, waitTime)
		moveServo(8, 2350, speed, waitTime)
		moveServo(9, 2250, speed, waitTime)

		time.sleep(waitTime)

		#moves body forward
		sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
		time.sleep(waitTime)

		#lifts up first leg 
		moveServo(25, 1600, speed, waitTime)
		moveServo(24, 1650, speed, waitTime)
		moveServo(25, 2215, speed, waitTime)

		#lifts up second leg 
		moveServo(1, 1535, speed, waitTime)
		moveServo(0, 1475, speed, waitTime)
		moveServo(1, 2150, speed, waitTime)

		#lifts up third leg 
		moveServo(17, 2500, speed, waitTime)
		moveServo(16, 1650, speed, waitTime)
		moveServo(17, 1600, speed, waitTime)

		#lifts up forth leg 
		moveServo(9, 1600, speed, waitTime)
		moveServo(8, 1650, speed, waitTime)
		moveServo(9, 2250, speed, waitTime)

		time.sleep(waitTime)

		#moves body forward
		sp.write(("#0 P1425 #8 P1500 #16 P1500 #24 P1600 #26 P1250 T400\r").encode())
		time.sleep(waitTime)

#the defult, rest position 
def defultPosition():

	# set the servos to the inital position
	sp.write("#0 P1425 #1 P2250 #2 P1625 #8 P1500 #9 P2300 #10 P1500 #16 P1500 #17 P1600 #18 P1475 #24 P1600 #25 P2215 #26 P1450 T.5\r".encode())

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