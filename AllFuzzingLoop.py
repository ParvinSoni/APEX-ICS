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
    S_Service_Id = b"\x11\x00"              # PlcShell
    S_Cmd_Id = b"\x01\x00"                  # Other
    S_Payload_Size = b"\x1c\x01\x00\x00"    # Calculated further
    #mutated_packet, num_mutations = bitflip_mutate(S_PlcShellMem_Payload_Tag4, fuzzebale = True)
    #mutated_packet, num_mutations = arithmetic_mutate(S_PlcShellMem_Payload_Tag4, fuzzeable = True)
    mutated_packet, num_mutations = radamsa_mutator(S_PlcShellReload_Payload_Tag4, fuzzeable = False)
    S_PlcShellReload_Payload_Tag4 = mutated_packet
    S_PlcShell_Payload  = S_PlcShell_Payload_Tag1 + S_Session_Id + S_PlcShell_Payload_Tag2 + S_PlcShellReload_Payload_Tag3 + S_PlcShellReload_Payload_Tag4
    mutated_packet_size = len(S_PlcShell_Payload)
    session_len = int(mutated_packet_size)
    S_Payload_Size = session_len.to_bytes(4, byteorder='little')
    S_Payload = S_PlcShell_Payload

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
    print('\033[91m' + "[+INFO] Fuzzed PLCShell Response: " + '\033[0m', FuzzedResponse)
    print("\n")
    TagValues = FindAndExtract(FuzzedResponse)
    #print("Tags:", TagValues)
    Store(TagValues)
    
    """
    if Response_Size == 36:           
        BlockDatagram = AckConstant()
        #  ++++++ Encapsulating upper 2 layers with ACK data, received by sock_ReceivingAck ++++++
        Channel_Acknowledge = BlockDatagram + b"\x80" + C_Version + C_ChannelId + C_AckNum
        #print('\033[92m' + "[+INFO] Sending (ACK) Packet" + '\033[0m')
        #socket_send(Channel_Acknowledge, sock)
        socket_dummy(Channel_Acknowledge, sock)
        if Counter == 1:               
            # close the socket connection         
            sock.close()
            # relaunch the script using subprocess
            subprocess.call(['python3', 'datagram.py'])
        else:
            pass
        Counter += 1
    else:
         pass"""