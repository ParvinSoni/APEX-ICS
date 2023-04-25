import hashlib
import json
import os

HashFile = 'hashes.json'

def StoreCodeSysHash(HashFile, ResponseHash, CodeSysPacket):
    # If the response hash doesn't already exist, store it in a new file
    if not os.path.exists(HashFile):
        with open(HashFile, 'w') as f:
            json.dump({ResponseHash: CodeSysPacket.decode()}, f)
            f.write('\n')
    else:
        # Check if the hash already exists in the file
        with open(HashFile, 'r') as f:
            if ResponseHash in f.read():
                return
        # If the hash does not exist, append it to the file
        with open(HashFile, 'a') as f:
            json.dump({ResponseHash: CodeSysPacket.hex()}, f)
            f.write('\n')


def Store(CodeSysPacket):
    # If the matching string is found, calculate and store the hash of the substring
    if CodeSysPacket is not None:
        # Calculating HASH of response packet (CodeSysPacket)
        SubstringHash = hashCalculate(CodeSysPacket)
        try:
            with open(HashFile, 'r') as f:
                FileContent = f.read().strip().split('\n')
                HashList = [json.loads(line) for line in FileContent]
        except FileNotFoundError:
            HashList = []
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            HashList = []
        if SubstringHash not in [list(hashDict.keys())[0] for hashDict in HashList]:
            HashDict = {SubstringHash: CodeSysPacket}
            StoreCodeSysHash(HashFile, SubstringHash, CodeSysPacket)
    return CodeSysPacket


def hashCalculate(CodeSysPacket):
    # Calculate the SHA256 hash of the response
    hash_obj = hashlib.sha256(CodeSysPacket)
    return hash_obj.hexdigest()   

def hashOperation_scoket(packet, sock):    
    MatchString  = b"\x00\x01\x17\xe8"
    sock.send(packet)
    
    print('Sending Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")
    
    NoCodeSysPacket = b""  # define variable outside of if block
    getTargetResponse = sock.recv(1024)
    first_call = False # update the variable value after first call
    # Find the index of the matching string in the response
    MatchIndex = getTargetResponse.find(MatchString)

    # If the matching string is not found, return None
    if MatchIndex == -1:
        NoCodeSysPacket = b""
    else:
        # Extract the substring from the matching index to the end of the response and return it
        print("Pattern Matched!!\n")
        CodeSysPacket = getTargetResponse[MatchIndex:]
    
    return CodeSysPacket

"""
def StoreCodeSysHash(HashDict, HashFile, ResponseHash):
    # If the response hash doesn't already exist, store it in the
    # hash dictionary and file
    if ResponseHash not in HashDict:
        HashDict[ResponseHash] = True
        with open(HashFile, 'a') as f:
            json.dump(HashDict, f, indent=None)
            f.write('\n')            

def Store(CodeSysPacket):

    # If the matching string is found, calculate and store the hash of the substring
    if CodeSysPacket is not None:
        # Calculating HASH of response packet (CodeSysPacket)
        SubstringHash = hashCalculate(CodeSysPacket)
        try:
            # If substring is not none, load JSON HashFile 
            with open(HashFile, 'r') as f:
                FileContent = f.read()
                HashDict = json.loads(FileContent) if FileContent else {}
        except FileNotFoundError:
            # If file isn't persent
            HashDict = {}
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            HashDict = {}
        try:
            StoreCodeSysHash(HashDict, HashFile, SubstringHash)
        except Exception as e:
            print(f"Error storing hash in JSON file: {e}")

    return CodeSysPacket
"""    