import socket
import threading
import RPi.GPIO as GPIO
import time
import datetime
from actuators import controller_larm

server_address = ('10.0.0.1', 12345)
client_address = ('10.0.0.2', 12346)

def send_hello(sock, message):
    hellos_sent = 0
    while hellos_sent < 100:
        hellos_sent += 1
        sock.sendto(message, client_address)
        time.sleep(3)
    print('sent', hellos_sent, 'hellos')

def ack_timer():
    global ACK_counter
    while True:
        ACK_counter += 1
        time.sleep(3)
        if ACK_counter > 3:
            print('Link appears to be dead')
            
def logging_time(network_time=None, system_time=None):
    if network_time:
        with open('./timestamps_wifi/timestamps_network', 'a') as file:
            network_time = str(network_time)
            file.write(network_time+'\n')
    
    if system_time:
        with open('./timestamps_wifi/timestamps_system', 'a') as file:
            system_time = str(system_time)
            file.write(system_time+'\n')
        

ACK_counter = 0


def main():
    global ACK_counter 

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    message=(b'hello')
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    hello_thread = threading.Thread(target=send_hello, args=(sock, message))
    hello_thread.start()

    timer_thread = threading.Thread(target=ack_timer)
    timer_thread.start()
    
    try:
        recv_one = False
        recv_counter = 0
        while True:
            data, address = sock.recvfrom(1024)
            end_time_net = time.time()
            print(data)
            data, start_time_sys, start_time_net = data.decode('utf-8').split('|')
            if data:
                # Do not timestamp if clearing buffer
                if not recv_one:
                    time_on_network = float(end_time_net) - float(start_time_net)
                    nettime_thread=threading.Thread(target=logging_time, args=(time_on_network, ))
                    print('time in network', str(time_on_network))
                    if not nettime_thread.is_alive() and recv_counter==0:
                        nettime_thread.start()

                ACK_counter = 0
                print(data)
                if data == '1' and not recv_one:
                    end_time_sys = time.time()
                    total_time = float(end_time_sys) - float(start_time_sys)
                    logging_time(system_time=total_time)
                    controller_larm()
                    # Clear buffer
                    recv_one = True
                    print('Time in system',total_time)

                if recv_one:
                    recv_counter += 1
                    if recv_counter > 2:
                        recv_counter = 0
                        recv_one = False

    except KeyboardInterrupt:
        #larm(on=False)
        pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        larm(on=False)
        exit()
