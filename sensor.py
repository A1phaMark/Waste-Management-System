import time
import socket
import RPi.GPIO as GPIO


def perform_reading():
	GPIO.setmode(GPIO.BCM)
        TRIG = 23
        ECHO = 24
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        GPIO.output(TRIG, False)
        time.sleep(2)
        GPIO.output(TRIG, True)
        time.sleep(.00001)
        GPIO.output(TRIG, False)
    
        # record the time duration GPIO.input is set to 1
        while GPIO.input(ECHO) == 0:
        	pulse_start = time.time()
        
        while GPIO.input(ECHO) == 1:
        	pulse_end = time.time()
    
        pulse_duration = pulse_end - pulse_start
        # calculate distance by (time*velocity)/2
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        GPIO.cleanup()
        print("distance recorded: " + str(distance))
        current_lev = 1 - (distance/std_height)
        current_lev = round(current_lev, 4)
	return current_lev


BUFFER_SIZE = 1024
std_height = 80 #Length of trash bin in cm

address = ('10.0.0.22', 8080)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(address)



while 1:
	try:
		print("Waiting for packet...")
		mess = s.recvfrom(1024)
		print(mess)
		send_addr = mess[1]
	
		# message = 1 means the Node tells the sensor to send a reading
		if mess[0].decode('utf-8') == '1':
			print("Receive request from head node, its time to perform a measurement!!")

			# perfrom a reading
			data = perform_reading()
			data = str(data).encode('utf-8')
			# send data to the head node	
			s.sendto(data, send_addr)
	
		# message = 0 means the Node has received the data
		if mess[0].decode('utf-8') == '0':
			print("Head node has received my data, its time to sleep~~",'\n')
			time.sleep(100)
	except:
		time.sleep(100)
		