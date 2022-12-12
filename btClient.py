#!/usr/bin/env python

import time 
import serial
import socket
import threading
import random
import os
import glob
import RPi.GPIO as GPIO

# Global
# Activate the DS1820 module
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
# our file name 28-00000ce54ab6
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Bluetooth
SERVER_MAC = 'dc:a6:32:9f:34:77'
PORT = 4
# Create bluetooth socket
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)


# Typical reading (raw file)
# crc=cyclic redundancy check
# 73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
# 73 01 4b 46 7f ff 0d 10 41 t=23187

def read_temp_raw():
    # Open device file and read lines, then return information
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    global temp_c
    temp_c = ''

    while True:
        start_time = str(time.time())
        # Get information from module
        lines = read_temp_raw()
        
         # Test again if crc error
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()

        # find position for t=
        equals_pos = lines[1].find('t=')
        # Check if =t not last position, then we know we have a temperature
        if equals_pos != -1:
            # Cleanup temp and create a message
            temp_string = lines[1][equals_pos+2:]
            end_time = time.time()
            temp_c = str((float(temp_string) / 1000.0))

            #timestamp = str((end_time - start_time))
            temp_c = temp_c + '|' + start_time

        time.sleep(1)
        
    """
    #print(lines)
    # Test again if crc error
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')
    # Check if we have a temp and divide by 1000 and return the temperature
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = str(float(temp_string) / 1000.0)
    """    
    

def main():
    """ Main function to control socket and calling for temperature"""
    global temp_c

    # Connect to master
    s.connect((SERVER_MAC, PORT))
    print(f'CONNECTED: {SERVER_MAC, PORT}')

    # Define and start temperature thread
    temp_thread = threading.Thread(target=read_temp)
    temp_thread.start()
    
    # First loop control
    first_loop = True
    message_sent = 0
    try:
        while message_sent < 100:
            """ Read temperature and send it to master""" 

            if first_loop:
                # Wait for first temp_c value
                first_loop = False
                time.sleep(2)

            # Get latest temp and timestamp since reading
            temp_c, timestamp_temperature = temp_c.split('|')
            
            if temp_c:
                # Send value
                print(f'[SENDING] VALUE: {temp_c}')
                #temp_c = str(temp_c)
            
                # Message (temp|start_time_system|start_time_network)
                message = (temp_c + '|' + timestamp_temperature + '|' + str(time.time()))
                s.send(bytes(message, 'UTF-8'))

            message_sent += 1 
            time.sleep(2)
       
        s.send(bytes('quit|None|None', 'UTF-8'))
        s.close()
        quit()

    except KeyboardInterrupt:
        # Send quit message
        s.send(bytes('quit', 'UTF-8'))
        s.close()
        quit()


if __name__ == '__main__':
    main()

