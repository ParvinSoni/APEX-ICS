import socket
import subprocess
from CRC32CheckSum import crc32_checksum
from Service_Layer_Commands import GetTargetIdent
from Hash_Operation import Store, hashOperation_scoket
from Mutator import *
from FeedBack import *
import time
import random
from Packet_Send import *
from Constants import *

#for id in range(1):
#print("Loop value is: \n", id)
# ------------------ Network Service With Channel Layer ------------------ #
random_id = random.randint(1, 255)
Id_Hex = hex(random_id)[2:].zfill(2)
Datagram = D_Magic + D_HopInfo + D_PktInfo + D_Service_Id + MsgId + D_Len + Sender + Receiver
Padding_1 = b"\x02\xc2\x00\x04"
Padding_2 = b"\xd2\x05\x0d"
# Id is filling below in the loop
channel =  Padding_1 + bytes.fromhex(Id_Hex) + Padding_2
Packet_Len = len(Datagram)+len(channel)
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Network_Service = Magic_Number+TotalBytes + Datagram +channel
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to Server
sock.connect((target_ip, target_port))    
print('\033[92m' + "[+INFO] Sending 1st Packet To Channel Layer" + '\033[0m')
socket_send(Network_Service, sock)
time.sleep(0.01)    

# ------------------ Open Channel With Channel Layer ------------------ #
#  ++++++ Preparing Datagram Layer  ++++++
Datagram = D_Magic + D_HopInfo + D_PktInfo + b"\x40" + MsgId + D_Len + Sender + Receiver

#  ++++++ Combining All Layers & Adding TotalBytes Field of Block Layer  ++++++
Packet_Len = len(Datagram)+len(Open_Chnl)+4+4
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Channel_Opening = Magic_Number+TotalBytes + Datagram + Open_Chnl    
print('\033[92m' + "[+INFO] Sending 2nd Packet To (Channel OPEN Channel)" + '\033[0m')
C_Version, ChannelId = socket_OpenChannel_c3(Channel_Opening, sock) # Sending Packet & collected last 4 byte from response of open channel packet of PLC    
time.sleep(0.01)

# ------------------ Open Channel With BLK Trans Channel Layer For (CmpDevice, GetTargetIdent) ------------- #

#  ++++++ Channel Layer  ++++++
C_Command_Id = b"\x01"
C_Flags = b"\x81"
C_ChannelId = ChannelId  

#  ++++++ Preparing Service Layer For GerTargetIdent Command  ++++++
Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_Cmd_Id+S_Session_Id+S_Payload_Size+S_Additional_Data+S_GettargetIndent_Payload    

#  ++++++ Preparing Channel Layer  ++++++
C_ChkSum = crc32_checksum(Service_Layer)
Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum

#  ++++++ Combining All Layers & Adding TotalBytes Field of Block Layer  ++++++
Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
BLK_Transmission = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer

#  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
RemNum += 1
C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
AckNum += 1    
C_AckNum = AckNum.to_bytes(4, byteorder='little')
print('\033[92m' + "[+INFO] Sending 3rd Packet To (CmpDevice GetTargetIdent)" + '\033[0m')
socket_send(BLK_Transmission, sock)

# ------------------ Session Create with BLK Trans Channel Layer For (CmpDevice, SessionCreate) ------------------ #

#  ++++++  Service Layer   ++++++ 
S_Session_Id = b"\x11\x00\x00\x00"
S_Payload_Size = b"\x88\x00\x00\x00"
Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_SessionCreate_Cmd+S_Session_Id+S_Payload_Size+S_Additional_Data+S_SessionCreate_Payload    

#  ++++++ Preparing Channel Layer  ++++++
C_ChkSum = crc32_checksum(Service_Layer) # CRC32 Calculation
Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum     

#  ++++++ Combining All Layers & Adding TotalBytes Field of Block Layer  ++++++
Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Session_Create = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer

#  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
RemNum += 1
C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
AckNum += 1    
C_AckNum = AckNum.to_bytes(4, byteorder='little')
print('\033[92m' + "[+INFO] Sending 4th Packet To (CmpDevice SessionCreate)" + '\033[0m')
S_Session_Id = socket_ServiceSessionCreate(Session_Create, sock)


# ------------------ Service Layer For (CmpDevice, LogIn) ------------------ #

#  ++++++ Preparing Datagram Layer  ++++++
Datagram = D_Magic + D_HopInfo + D_PktInfo + b"\x40" + MsgId + D_Len + Sender + Receiver

#  ++++++ Preparing Channel Layer & adding service tag to service layer   ++++++
S_Payload_Size = b"\x10\x00\x00\x00"
S_SessionTags = b"\x22\x84\x80\x00\x02\x00\x00\x00\x25\x84\x80\x00\x01\x00\x00\x00"

#  ++++++ Service Layer  ++++++
Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_SessionCreate_Cmd_Login+S_Session_Id+S_Payload_Size+S_Additional_Data+S_SessionTags    

#  ++++++ Channel Layer  ++++++
C_ChkSum = crc32_checksum(Service_Layer) 
Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum

#  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
RemNum += 1
C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
AckNum += 1    
C_AckNum = AckNum.to_bytes(4, byteorder='little')     
        
#  ++++++ Combining DATAGRAM + CHANNEL + SERVICE & calculating packet size for TotalByte field of Block Layer  ++++++
Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Session_LogIn = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer
time.sleep(0.03)
#AckData, KeepAliveData = sock_ReceivingAck(Session_LogIn, sock)
#KeepAliveData = sock_ReceivingAck(Session_LogIn, sock)
print('\033[92m' + "[+INFO] Sending 5th Packet To (CmpDevice LogIn)" + '\033[0m')
sock_ReceivingAck(Session_LogIn, sock)

# ------------------ Sending ACK of RunTime's Response ------------------ #
#  ++++++ From socket_SendResponseAck() grabbing whole Block & Datagram layer  ++++++
BlockDatagram = AckConstant()
#  ++++++ Encapsulating upper 2 layers with ACK data, received by sock_ReceivingAck ++++++
Channel_Acknowledge = BlockDatagram + b"\x80" + C_Version + C_ChannelId + C_AckNum
print('\033[92m' + "[+INFO] Sending 6th Packet (ACK)" + '\033[0m')
socket_send(Channel_Acknowledge, sock)


# ------------------ Service Layer For (2nd CmpDevice, LogIn) ------------------ #

#  ++++++ Preparing Datagram Layer  ++++++
Datagram = D_Magic + D_HopInfo + D_PktInfo + b"\x40" + MsgId + D_Len + Sender + Receiver

#  ++++++ Preparing Channel Layer  ++++++
C_Command_Id = b"\x01"
C_Flags = b"\x81"
C_ChannelId = ChannelId

#  ++++++ Preparing Channel Layer & adding service tag to service layer   ++++++
S_Cmd_Id = b"\x02\x00" # LogIn
S_Payload_Size = b"\x1c\x01\x00\x00"
print("S_Paylod is: ", S_SecondLogIn_Payload)
mutated_packet, num_mutations = bitflip_mutate(S_SecondLogIn_Payload, fuzzeable = False)
mutated_packet_size = len(mutated_packet)
session_len = int(mutated_packet_size)
S_Payload_Size = session_len.to_bytes(4, byteorder='little')
S_SecondLogIn_Payload = mutated_packet

#  ++++++ Service Layer  ++++++
Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_Cmd_Id+S_Session_Id+S_Payload_Size+S_Additional_Data+S_SecondLogIn_Payload    

#  ++++++ Channel Layer  ++++++
C_ChkSum = crc32_checksum(Service_Layer) # CRC32 Calculation
C_RemainingDataSize = C_AckNum
Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum

#  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
RemNum += 1
C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
AckNum += 1    
C_AckNum = AckNum.to_bytes(4, byteorder='little')     
        
#  ++++++ Combining DATAGRAM + CHANNEL + SERVICE & calculating packet size for TotalByte field of Block Layer  ++++++
Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Session_LogIn = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer    
time.sleep(0.03)

#  ++++++  Send the mutated packet  ++++++ 
#response = sendFuzz(Session_LogIn, sock, num_mutations)
print('\033[92m' + "[+INFO] Sending 7th Packet (CmpDevice, LogIn)" + '\033[0m')
sock_ReceivingAck(Session_LogIn, sock)


# ------------------ Service Layer For (CmpDevice, GetOperatingIdent) ------------------ #
#  ++++++ Preparing Datagram Layer  ++++++
Datagram = D_Magic + D_HopInfo + D_PktInfo + b"\x40" + MsgId + D_Len + Sender + Receiver

#  ++++++ Preparing Channel Layer  ++++++
C_Command_Id = b"\x01"
C_Flags = b"\x81"
C_ChannelId = ChannelId

#  ++++++ Preparing Channel Layer & adding service tag to service layer   ++++++
S_Service_Id = b"\x01\x00"             
S_Cmd_Id = b"\x07\x00"               
#S_Session_Id = ExtractedS_Session_Id
S_Payload_Size = b"\x00\x00\x00\x00"   
S_Payload = b"\x00\x00\x00\x00"

#  ++++++ Service Layer  ++++++
Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_Cmd_Id+S_Session_Id+S_Payload_Size+S_Payload    

#  ++++++ Channel Layer  ++++++
C_ChkSum = crc32_checksum(Service_Layer) 
C_AckNum = C_RemainingDataSize
Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum

#  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
RemNum += 1
C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
AckNum += 1    
C_AckNum = AckNum.to_bytes(4, byteorder='little')     
        
#  ++++++ Combining DATAGRAM + CHANNEL + SERVICE & calculating packet size for TotalByte field of Block Layer  ++++++
Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Session_GetOperatingIdent = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer    
time.sleep(0.03)

#  ++++++  Send the mutated packet  ++++++ 
print('\033[92m' + "[+INFO] Sending 8th Packet (CmpDevice, GetOperatingIdent)" + '\033[0m')
socket_dummy(Session_GetOperatingIdent, sock)

# ------------------ Service Layer For (CmpDevice, PlcShell) ------------------ #
#  ++++++ Preparing Datagram Layer  ++++++
Datagram = D_Magic + D_HopInfo + D_PktInfo + b"\x40" + MsgId + D_Len + Sender + Receiver

#  ++++++ Preparing Channel Layer  ++++++
C_Command_Id = b"\x01"
C_Flags = b"\x81"
C_ChannelId = ChannelId

#  ++++++ Preparing Channel Layer & adding service tag to service layer   ++++++
S_Service_Id = b"\x11\x00"          
S_Cmd_Id = b"\x01\x00" 
#S_Session_Id = ExtractedS_Session_Id
S_Payload_Size = b"\x1c\x01\x00\x00"    # Calculated further
mutated_packet, num_mutations = bitflip_mutate(S_PlcShellChanID_Payload_Tag3, fuzzeable = False)
S_PlcShellChanID_Payload_Tag3 = mutated_packet
S_PlcShellPID_Payload  = S_PlcShell_Payload_Tag1 + S_Session_Id + S_PlcShell_Payload_Tag2 + S_PlcShellChanID_Payload_Tag3
mutated_packet_size = len(S_PlcShellPID_Payload)
session_len = int(mutated_packet_size)
S_Payload_Size = session_len.to_bytes(4, byteorder='little')
S_Payload = S_PlcShellPID_Payload

#  ++++++ Service Layer  ++++++
Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_Cmd_Id+S_Session_Id+S_Payload_Size+S_Additional_Data+S_Payload    

#  ++++++ Channel Layer  ++++++
C_ChkSum = crc32_checksum(Service_Layer) # CRC32 Calculation
C_AckNum = C_RemainingDataSize
Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum

#  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
RemNum += 1
C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
AckNum += 1    
C_AckNum = AckNum.to_bytes(4, byteorder='little')     
        
#  ++++++ Combining DATAGRAM + CHANNEL + SERVICE & calculating packet size for TotalByte field of Block Layer  ++++++
Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
Session_LogIn = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer    
time.sleep(0.03)

#  ++++++  Send the mutated packet  ++++++ 
#response = sendFuzz(Session_LogIn, sock, num_mutations)
print('\033[92m' + "[+INFO] Sending 9th Packet (CmpDevice, PlcShell)" + '\033[0m')
a=socket_send(Session_LogIn, sock)
print("PLCShell: ", a)

Counter = 0
while True:
    # ------------------ Service Layer For (CmpDevice, PlcShell) ------------------ #
    #  ++++++ Preparing Datagram Layer  ++++++
    Datagram = D_Magic + D_HopInfo + D_PktInfo + b"\x40" + MsgId + D_Len + Sender + Receiver

    #  ++++++ Preparing Channel Layer  ++++++
    C_Command_Id = b"\x01"
    C_Flags = b"\x81"
    C_ChannelId = ChannelId

    #  ++++++ Preparing Channel Layer & adding service tag to service layer   ++++++
    S_Service_Id = b"\x11\x00"
    S_Cmd_Id = b"\x01\x00"  
    S_Payload_Size = b"\x1c\x01\x00\x00"  
    mutated_packet, num_mutations = radamsa_mutator(S_PlcShellPID_Payload_Tag3, fuzzeable = True)
    S_PlcShellChanID_Payload_Tag3 = mutated_packet
    S_PlcShellPID_Payload  = S_PlcShell_Payload_Tag1 + S_Session_Id + S_PlcShell_Payload_Tag2 + S_PlcShellChanID_Payload_Tag3
    mutated_packet_size = len(S_PlcShellPID_Payload )
    session_len = int(mutated_packet_size)
    S_Payload_Size = session_len.to_bytes(4, byteorder='little')
    S_Payload = S_PlcShellPID_Payload 

    #  ++++++ Service Layer  ++++++
    Service_Layer = S_Proto_Id+S_Hdr_Size+S_Service_Id+S_Cmd_Id+S_Session_Id+S_Payload_Size+S_Additional_Data+S_Payload    

    #  ++++++ Channel Layer  ++++++
    C_ChkSum = crc32_checksum(Service_Layer) # CRC32 Calculation
    C_AckNum = C_RemainingDataSize
    Channel_BLK_Trans = C_Command_Id+C_Flags+C_Version+C_ChannelId+C_AckNum+C_RemainingDataSize+C_ChkSum

    #  ++++++ Increament for C_RemainingDataSize AND C_AckNum  ++++++
    RemNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
    RemNum += 1
    C_RemainingDataSize = RemNum.to_bytes(4, byteorder='little')
    AckNum = int.from_bytes(C_RemainingDataSize, byteorder="little")
    AckNum += 1    
    C_AckNum = AckNum.to_bytes(4, byteorder='little')     
            
    #  ++++++ Combining DATAGRAM + CHANNEL + SERVICE & calculating packet size for TotalByte field of Block Layer  ++++++
    Packet_Len = len(Datagram) + len(Channel_BLK_Trans) + len(Service_Layer)+8
    TotalBytes = Packet_Len.to_bytes(4, byteorder='little')
    Session_LogIn = Magic_Number + TotalBytes + Datagram + Channel_BLK_Trans + Service_Layer    
    #time.sleep(0.3)

    #  ++++++  Send the mutated packet  ++++++ 
    #response = sendFuzz(Session_LogIn, sock, num_mutations)
    print('\033[92m' + "[+INFO] Sending Fuzzed Packet (CmpDevice, PlcShell)" + '\033[0m')
    FuzzedResponse, Response_Size  = socket_SendFuzzed(Session_LogIn, sock)
    Counter += 1
    print('\033[91m' + "[+INFO] Fuzzed PLCShell Response: " + '\033[0m', FuzzedResponse)
    print("\n")
    TagValues = FindAndExtract(FuzzedResponse)
    Store(TagValues)
    print("Number of packets:", Counter)
