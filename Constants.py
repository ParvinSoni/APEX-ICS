target_ip = '192.168.1.102'
target_port = 11740
hash_file = 'hashes.json'
MatchString  = b"\x00\01\x17\e8"
first_call = True

# ------------------------------ CmpBlkDrvTcp (Block Layer) ----------------------------- #
Magic_Number = b"\x00\x01\x17\xe8"

# ------------------------------ (Datagram Layer) ----------------------------- #
D_Magic = b"\xc5"
D_HopInfo = b"\x6b"
D_PktInfo = b"\x40"
D_Service_Id = b"\x03"                 
MsgId = b"\x00"
D_Len = b"\x43"
Sender = b"\x2d\xdc\xc0\xa8\x01\x66"
Receiver = b"\x00\x00\xc0\xa8\x38\x01\x03\xfa"

# ------------------------------ (Channel Layer) ----------------------------- #
C_Command_Id = b"\xc3"
C_Flags = b"\x00"
C_Version  = b"\x02\x01"
C_Command_Data = b"\xfc\x0e\x64\x68\x67\x30\x7a\xf7\x00\x40\x1f\x00\x08\x00\x00\x00"
Open_Chnl = C_Command_Id + C_Flags + C_Version + C_Command_Data
C_AckNum = b"\x01\x00\x00\x00"              
C_RemainingDataSize = b"\x00\x00\x00\x00"   

# ------------------------------ (Service Layer) ----------------------------- #
S_Proto_Id = b"\x55\xcd"
S_Hdr_Size = b"\x10\x00"
S_Service_Id = b"\x01\x00"              
S_Cmd_Id = b"\x01\x00"                  
S_SessionCreate_Cmd = b"\x0a\x00"       
S_SessionCreate_Cmd_Login = b"\x02\x00" 
S_Session_Id = b"\x00\x00\x00\x00"
S_Payload_Size = b"\x10\x00\x00\x00"
S_Additional_Data = b"\x00\x00\x00\x00"
S_GettargetIndent_Payload = b"\x01\x8c\x80\x00\x06\x10\x00\x00\x10\x00\x00\x00\x00\x00\x07\x04"
S_SessionCreate_Payload = b"\x83\x01\xfc\x00\x40\x84\x80\x00\x50\x51\xde\xc0\x41\x88\x80\x00\x43\x4f\x44\x45\x53"\
                b"\x59\x53\x00\x42\x9c\x80\x00\x43\x4f\x44\x45\x53\x59\x53\x20\x44\x65\x76\x65\x6c\x6f\x70\x6d\x65\x6e\x74\x20\x47\x6d\x62\x48\x00\x00\x00\x00\x44\x9c\x80\x00\x43\x4f\x44" \
                b"\x45\x53\x59\x53\x20\x56\x33\x2e\x35\x20\x53\x50\x31\x38\x20\x50\x61\x74\x63\x68\x20\x34\x00\x00\x00\x43\x94\x80\x00\x44\x45\x53\x4b\x54\x4f\x50\x2d\x30\x50\x4f\x46\x4e\x37" \
                b"\x47\x2e\x00\x00\x00\x00\x45\x8c\x80\x00\x33\x2e\x35\x2e\x31\x38\x2e\x34\x30\x00\x00\x00" \
                b"\x46\x84\x80\x00\x03\x00\x00\x00"
S_SecondLogIn_Payload = b"\x22\x84\x80\x00\x02\x00\x00\x00\x25\x84\x80\x00\x02\x00\x00\x00" \
                b"\x81\x01\x88\x02\x10\x02\x00\x00"


# PLCShell "Contant Tags" Command. 
S_PlcShell_Payload_Tag1 = b"\x11\x84\x80\x00"
S_PlcShell_Payload_Tag2 = b"\x13\x84\x80\x00\x00\x00\x00"

# PLCShell "pid" Command. 
# -- Fixed (Can be used for Fuzzing)
S_PlcShellPID_Payload_Tag3 = b"\x00\x10\x06\x70\x69\x64\x00\x00\x00" 

# PLCShell "Channel Info" Command. 
# -- Fixed (Can be used for Fuzzing)
S_PlcShellChanID_Payload_Tag3 = b"\x00\x10\x0e\x63\x68\x61\x6e\x6e\x65\x6c\x69\x6e\x66\x6f\x00\x00\x00" 

# PLCShell "Mem" Command. 
# -- Fixed (Can be used for Fuzzing)
S_PlcShellMem_Payload_Tag3 = b"\x00\x10\x06\x6d\x65\x6d\x00\x00\x00" + b"\x12\x0a" 
S_PlcShellMem_Payload_Tag4 = b"\x20\x32\x68\x61\x6e\x6e\x65\x6c\x69\x6e"

# PLCShell "reload Application"
# -- Fixed 
S_PlcShellReload_Payload_Tag3 = b"\x00\x10\x0a\x72\x65\x6c\x6f\x61\x64\x00\x00\x00\x00" + b"\x12\x0e" 
# -- (Can be used for Fuzzing)
S_PlcShellReload_Payload_Tag4 = b"\x41\x70\x70\x6c\x69\x63\x61\x74\x69\x6f\x6e\x00\x00\x00" 

# Set Node Name
S_RenameNode_Payload_Tag1 = b"\x58\xc0\x80\x00"
S_RenameNode_Payload_Tag2 = b"\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08"
