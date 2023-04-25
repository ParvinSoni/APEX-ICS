import socket
import time 

def socket_dummy(packet, sock):    
    sock.send(packet)
    
    print('Sending Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")

    Response = sock.recv(1024)
    print("CmpLogin Response:",Response)

def socket_normal(packet, sock):    
    sock.send(packet)
    
    print('Sending Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")

    Response = sock.recv(1024)
    print("CmpLogin Response:",Response)
    _ = Response

def socket_send(packet, sock):    
    global first_call 
    MatchString  = b"\x00\x01\x17\xe8"
    time.sleep(0.1)
    sock.send(packet)
    
    print('Sent Payload: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")
    
    first_call = True
    if first_call:
        _ = sock.recv(1024)
        first_call = False 
    else:
        pass 

def socket_SendFuzzed(packet, sock):    
    global first_call 
    sock.send(packet)
    
    for b in packet:
        print(f'{b:02x}', end=' ')
    
    first_call = True
    if first_call:
        getTargetResponse = sock.recv(1024)
        size = len(getTargetResponse)
        first_call = False 
    else:
        pass 
    return getTargetResponse, size


def socket_OpenChannel_c3(packet, sock):
    sock.send(packet)
    
    print('Sending Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")

    responseOpenChannel_c3 = sock.recv(1024)
    last_four_bytes = responseOpenChannel_c3[-4:]
    chan_id = responseOpenChannel_c3[-14:-12] 
    return (chan_id, last_four_bytes)

def socket_ServiceSessionCreate(SessionCreate, sock):
    sock.send(SessionCreate)    
    print('Sending Packet: \n', end='')
    for b in SessionCreate:
        print(f'{b:02x}', end=' ')
    print("\n")
    responseServiceSessionCreate = sock.recv(1024)
    session_id = responseServiceSessionCreate[-12:-8]
    return (session_id)


def sock_ReceivingAck(packet, sock):
    sock.send(packet)    
    print('Sending Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")
    try:
        _ = sock.recv(1024)        
    except Exception as e:
        print(f"Error receiving response: {e}")
        return None

def AckConstant():
    # ACK C_CommandId is already added
    return b"\x00\x01\x17\xe8\x28\x00\x00\x00\xc5\x6b\x40\x40\x00\x43\x2d\xdc\xc0\xa8\x01\x66\x00\x00\xc0\xa8\x38\x01\x03\xfa"+b"\x02"

def KeepAliveConstant():
    # KEEP ALIVE C_CommandId is already added
    return b"\x00\x01\x17\xe8\x28\x00\x00\x00\xc5\x6b\x40\x40\x00\x43\x2d\xdc\xc0\xa8\x01\x66\x00\x00\xc0\xa8\x38\x01\x03\xfa"+b"\x03"
