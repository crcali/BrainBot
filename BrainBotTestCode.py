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
sp.write("#17 P2425\r".encode())
sp.write("#18 P1475\r".encode())
sp.write("#24 P1500\r".encode())
sp.write("#25 P2215\r".encode())
sp.write("#26 P1450\r".encode())

#sets up the move forward module 
def moveForward(speed, distance):
	#commands to move forward with the parameters
	sp.write(("#1 P2000 s%i\r" %speed).encode())
	sp.write("#0 P2000 s750\r".encode())
	sp.write("#25 P2000 s750\r.".encode())
	sp.write("#24 P1300 s750\r".encode())
	time.sleep(2)
	sp.write("#1 P2150 s750\r".encode())
	sp.write("25 P2215 s750\r".encode())
	time.sleep(5)
	sp.write("#17 P2600 s750\r".encode())
	sp.write("#16 P500 s750\r".encode())
	sp.write("#9 P2500 s750\r".encode())
	sp.write("#8 P1800 s750\r".encode())
	time.sleep(2)
	sp.write("#17 P2425 s750\r".encode())
	sp.write("#9 P2300 s750\r".encode())

	time.sleep(10)

	sp.write("#0 P1425 s750\r".encode())
	sp.write("#1 P2150 s750\r".encode())
	sp.write("#2 P1625 s750\r".encode())
	sp.write("#8 P1500 s750\r".encode())
	sp.write("#9 P2300 s750\r".encode())
	sp.write("#10 P1500 s750\r".encode())
	sp.write("#16 P1500 s750\r".encode())
	sp.write("#17 P2425 s750\r".encode())
	sp.write("#18 P1475 s750\r".encode())
	sp.write("#24 P1500 s750\r".encode())
	sp.write("#25 P2215 s750\r".encode())
	sp.write("#26 P1450 s750\r".encode())

def moveBackward(speed, distance):
	#commands to move backward with the parameters
	print "moveBackward"

while True: 
	command = raw_input("Enter moveForward or moveBackward: ")
	speed = input("Please enter the desired speed in feet per second: ")
	distance = input("Please enter the number of feet you wish the robot to move: ")

	print ("Inputed Command: %s \n" % command)

	if command == "moveForward":
	#run the moveforward module

		print "initiating command\n"

		moveForward(speed, distance)

		print "finsihed command; restarting and waiting for another input \n"
		
#close serial port
sp.close()