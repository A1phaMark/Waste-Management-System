import socket
import sys
import time

# node file
server_address=('10.0.0.157', 8080)      # head node address
sensor_address = [('10.0.0.22', 8080)]   # a list of all sensor addresses
last_lev = 0
last_time = time.time()

############## update to the server####################################
def _update(pack):
    try:
        print("Sending update now...")
        print("Trying to connect with TCP server...")
        ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts.connect(("TCP server IP", 80))
        ack = ts.recv(1024)
        print("Connection with server success! Sending data now...")
        print(ack.decode("utf-8"))

        ts.send(pack.encode('utf-8'))
        mess = ts.recv(1024)
        print(mess.decode("utf-8"))
        print("Data Transfer finished! Now go to sleep...")
        ts.close()
        return 1

    except:
        print("Cannot connect to TCP server, go to sleep and wait for next data transfer...")
        return 0



############# make the packet ################################################################
def make_pack(data):
    data = str(data)
    device_name = 'id001'  # represent trash can id
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    pak = data + ', ' + device_name + ', ' + t
    return pak



############ main ##############################################################
while 1:
    data = 0
    sensor_count = 0

    for addr in sensor_address:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(server_address)

            # sending request to sensor
            message = '1'
            print("Trying to send to sensor", sensor_count+1, "...")
            s.sendto(message.encode('utf-8'), addr)

            # receive packet from sensor
            reply = s.recvfrom(1024)
            print(reply)
            temp = reply[0]
            data += float(temp.decode('utf-8'))
            print("Received data from sensor, sending a reply...")

            # sending reply to inform sensor that the packet is received
            message = '0'
            s.sendto(message.encode('utf-8'), addr)
            print("Reply sent")
            sensor_count+=1

        except:
            print("An error occur while trying to get data from sensor...")

    print('')

    print("Received data from all sensors, processing data now...")

    try:
        current_lev = data/sensor_count

        # in our test, we made the interval much smaller
        if current_lev < 0.5:
            interval = 7200
        elif current_lev >= 0.8:
            interval = 1800
        else:
            interval = 3600


        timer = time.time()
        timer-= last_time
        if timer >= interval:
            #make the data packet
            pack = make_pack(current_lev)
            # Update to server complete
            if _update(pack) == 1:
                last_time = time.time()   # reset timer
                last_lev = current_lev    # update last level
            # update to server failed
            else:
                last_lev = current_lev
        else:
            change_lev = current_lev - last_lev
            
	    # check if the load changes a lot in a short period of time
	    if change_lev >= 0.25:
                # make the data packet
                pack = make_pack(current_lev)
                if _update(pack) == 1:
                    last_time = time.time()
                    last_lev = current_lev
                else:
                    last_lev = current_lev
            else:
                print("No need to send update now, go to sleep...")
                last_lev = current_lev
    except:
        print("Error occured while processing the data")
    print("----------------------------------------------------------------", '\n')
    time.sleep(10)
