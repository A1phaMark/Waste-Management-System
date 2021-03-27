import time
import socket
import RPi.GPIO as GPIO

TCP_IP = ' ' #Put IP addr here
TCP_PORT =   #Put port # here
BUFFER_SIZE = 1024
STANDARD_SIZE = 80 #Length of trash bin in cm

current_lev = 0

while (1):
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
    
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    GPIO.cleanup()
    print("distance recorded: " + str(distance))
    current_lev = 1 - (distance/STANDARD_SIZE)
    current_lev = round(current_lev, 4)
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    MESSAGE = str(current_lev) + ", id00x, " + timestamp #put id number of sensor at id00x
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    ack = s.recv(BUFFER_SIZE)
    print(ack.decode('utf-8'))
    s.sendall(MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)
    print("recieved data:", data.decode('utf-8'))
    s.close()

    #Can put custom time intervals based on needs
    if current_lev < 0.5:
        interval = 7200   # 2 hours
    elif current_lev >= 0.8:
        interval = 1800   # 30 mins
    else:
        interval = 3600   # 1 hour

    time.sleep(interval)
