import socket
import threading
import time
from actuators import larm, warning_led, controller_larm
from logging_influxdb import add_influxdb

HOST_MAC = 'DC:A6:32:9F:34:77'
PORT = 4 
BACKLOG = 1
SIZE = 1024

NUMBER_CYCLES = 5
TIMER_CYCLE = 5
cycle = 0

TEMP_THRESH = 24


def start_larm():
    controller_larm()


def server():
    """ Start bluetooth server"""
    global cycle

    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.bind((HOST_MAC, PORT))
    s.listen(BACKLOG)

    try:
        # Accept client
        client, address = s.accept()
        print(f"{address} CONNECTED")
        
        timer_on = False
        message_number = 0
        while True:
            # Listen for data
            data = client.recv(SIZE)
            value, timestamp_temperature, timestamp_network = data.decode('utf-8').split('|')
            end_time_network = time.time()

            if value == 'quit':
                client.close()
                s.close()
                break
            message_number += 1

            time_on_network = (end_time_network - float(timestamp_network))
            thread_time_log = threading.Thread(target=logging_timestamps, args=(time_on_network,))
            if not thread_time_log.is_alive():
                thread_time_log.start()
            print(f'NETWORK DELAY: {time_on_network}')

            #print(value, timestamp_temperature, timestamp_netwok)
            
            if not timer_on:
                warning_timer = threading.Timer(10, controller_larm)
        
            if value:
                # Reset cycle counter
                cycle = 0
                print(value)
                #client.send(data)

                # Check data
                
                if float(value) >= TEMP_THRESH:
                    #larm(on=True)
                    
                    if not warning_timer.is_alive() and not timer_on:
                        print('[WARNING] timer started')
                        warning_led()
                        warning_timer.start()
                        timer_on = True
                    
                        end_time_system = time.time()
                        time_on_system = (end_time_system - (float(timestamp_temperature) + time_on_network))
                        logging_timestamps(system_time=time_on_system)
                        print(f'SYSTEM DELAY: {time_on_system}')

                else:
                    #if warning_timer.is_alive():
                    #print('[WARNING RESET] Timer reset')
                    warning_timer.cancel()
                    warning_led(on=False)
                    timer_on = False
                
                call_logging(value)

        print(message_number)

    except KeyboardInterrupt:
        print("Closing socket")
        client.close()
        s.close()
        quit()


def call_logging(value):
    """
    exampledata
    {
    'sensors':
    [{'sensor': 'interior', 'value': -10.45, 'unit': 'C'},
    {'sensor': 'exterior', 'value': -3.41, 'unit': 'C'}]
    }
    """
    
    data = {'sensor': 'DS1820', 'value': str(value), 'unit': 'C'}
    add_influxdb(data)

    
def logging_timestamps(network_time=None, system_time=None):

    if network_time:
        with open('./timestamps_bt/timestamps_network.txt', 'a') as file:
            network_time = str(network_time)
            file.write(network_time+'\n')

    if system_time:
        with open('./timestamps_bt/timestamps_system.txt', 'a') as file:
            system_time = str(system_time)
            file.write(system_time+'\n')


def check_cycles():
    """ Cycle to check if we still recieves messages"""
    global cycle 

    
    while cycle < NUMBER_CYCLES:
        #print(cycle)

        cycle += 1
        time.sleep(TIMER_CYCLE)

    print('[CONNECTION LOST] Starting larm')
    controller_larm()



def main():
    # Threads
    thread_server = threading.Thread(target=server)
    thread_cycle = threading.Thread(target=check_cycles)

    try:
        thread_server.start()
        thread_cycle.start()
    except:
        return None




if __name__ == '__main__':
    
    try:
        main()
       
    except KeyboardInterrupt:
        s.close()
        exit()


    
    



