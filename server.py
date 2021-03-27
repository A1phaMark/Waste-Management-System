#! /user/bin/env python3
# Feiyang Yu  2021/3/24
import socket
import pyodbc


####################################################
# Create new table for new devices
def create_new_table(device_name, cursor):
    cursor.execute('SELECT COUNT(*) FROM device')
    num_of_row = cursor.fetchval()
    new_table_name = "table" + str(num_of_row + 1)
    print(new_table_name)

    # update device table
    cursor.execute('INSERT INTO device VALUES (\'' + device_name + '\', \'' + new_table_name + '\')')
    # create a device to store data for new device
    cursor.execute('CREATE TABLE '+ new_table_name +'(Device_Name char(10) NOT NULL, Load float NOT NULL,Time datetime);')
    cursor.commit()

################################################################


#####################################################
# Update sensor data to SQL database
def update_db(lev, device_name, time):
    print("Trying to update the database ...")
    lev = str(lev)
    now = time

    server = 'sql server name'
    database = 'Sensor_Log'
    db = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                        'SERVER=' + server + ';'
                        'DATABASE=' + database + ';'
                        'Trusted_connection=yes;'
                        )
    cursor = db.cursor()

    # check if device is in the database
    cursor.execute('SELECT COUNT(*) FROM device WHERE device_name = \'' + device_name + '\'')
    counter = cursor.fetchval()

    # if the device is not in the database, create a table for this device
    if counter == 0:
        print("No device found in database")
        create_new_table(device_name, cursor)

    cursor.execute('SELECT table_name FROM device WHERE device_name = \'' + device_name + '\'')
    table_name = cursor.fetchval()
    print("Creating a new table for "+device_name+" , new table name: "+table_name)
    cursor.execute('INSERT INTO ' + table_name + ' VALUES (\'' + device_name + '\', \'' + lev + '\', \'' + now + '\');')

    db.commit()

    print("Database update Complete!")


################################################################
##############################################################
############ main function  #########################
HOST = socket.getaddrinfo(socket.gethostname(), 80)
HOST_name = socket.gethostname()
print(HOST_name)


# create ipv4 socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("10.0.0.157", 80))
s.listen(1)

# looking for TCP connection request
while 1:
    print("waiting for client connection")
    try:
        client, client_address = s.accept()
        print("client name: ", client)
        print("client ip: ", client_address)
        client.send((bytes("I received your connection request", "utf-8")))

        # receive data from sensor
        buffer = client.recv(1024)

        # decode buffer into the data we need
        data = buffer.decode("utf-8")
        # get trash can level
        for a in range(0, len(data)):
            if data[a] == ',':
                break
        lev = data[:a]
        lev = float(lev)
        # get device name
        for b in range(a+1, len(data)):
            if data[b] == ',':
                break
        device_name = data[a+2:b]
        #get time
        time = data[b+2:len(data)]


        print("Device name: ", device_name)
        print("Level: ", lev)
        print("TIme: ", time)

        print("Packat reveiced : ", data, "\n")
        client.send((bytes("Data update received", "utf-8")))
        client.close()
        print("Close connection with ", client, '\n')
        update_db(lev, device_name, time)
        print('#################################################################################', '\n')

    except:
        client.close()
        print("Close connection with ", client,'\n')

