from Mutator import *
import socket
import time
from Hash_Operation import *


# Define based on grammar. 
from BachMann_Constant import *

def SendPkt(packet, sock):    
    #time.sleep(0.2)
    sock.send(packet)
    
    print('Sending Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")

    Response = sock.recv(1024)
    return Response

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to Server
sock.connect((target_ip, target_port))    

while True:
    Cmp_mjsys = Cmp_mjsys_Cnst
    mutated_packet, num_mutations = radamsa_mutator(Cmp_mjsys_Name, fuzzeable = True)    
    Cmp_mjsys += mutated_packet + Cmp_AdditionalData
    print('\033[91m' + "[+INFO] Fuzzed Packet: " + '\033[0m', mutated_packet)
    FuzzedResponse = SendPkt(Cmp_mjsys, sock)
    print('\033[91m' + "[+INFO] Fuzzed Response: " + '\033[0m', FuzzedResponse)

