import random
import time
import subprocess

# Define the mutation rate (percentage of bits to be flipped)
mutation_rate = 10

# For bit flip fuzzing
def bitflip_mutate(packet, fuzzeable):
    if not fuzzeable:
        return packet, 0    
    mutation = bytearray(packet)
    num_mutations = 0
    for i in range(len(packet)):
        bit = 1
        for j in range(8):
            if random.randint(0, 99) < mutation_rate:
                mutation[i] ^= bit
                num_mutations += 1
            bit <<= 1
    return bytes(mutation), num_mutations

def byteflip_mutate(packet, fuzzeable):
    if not fuzzeable:
        return packet, 0
    
    # Convert packet bytes to a list of integers
    nums = [int.from_bytes(packet[i:i+1], byteorder='little', signed=False) for i in range(0, len(packet))]
    
    # Flip a random bit in each number
    num_mutations = 0
    for i in range(len(nums)):
        if random.randint(0, 99) < mutation_rate:
            # Flip a random bit in the number
            bit_to_flip = random.randint(0, 7)
            nums[i] ^= (1 << bit_to_flip)
            num_mutations += 1
    
    # Convert the mutated numbers back to bytes and return
    mutated_packet = b''
    for n in nums:
        mutated_packet += n.to_bytes(1, byteorder='little', signed=False)
 
    return mutated_packet, num_mutations

def radamsa_mutator(packet, fuzzeable):
    # If Boolean value is False
    if not fuzzeable:
        return packet, 0        
    # Use Radamsa to generate a mutated packet value
    while True:
        p = subprocess.Popen(['radamsa', '-n', '2'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        mutated_packet, _ = p.communicate(input=packet)
        mutated_packet = mutated_packet.strip()
        # Calculate the number of mutations performed
        num_mutations = mutated_packet.count(b'MUTATED BY RADAMSA')
        # Check the length of the mutated packet and truncate it if necessary
        if len(mutated_packet) > 400:
            mutated_packet = mutated_packet[:400]
        # Return the mutated packet and the number of mutations performed
        return mutated_packet, num_mutations


"""def radamsa_mutator(packet, fuzzeable):
    # If Boolean value is False
    if not fuzzeable:
        return packet, 0        
    # Use Radamsa to generate a mutated packet value
    while True:
        p = subprocess.Popen(['radamsa', '-n', '2'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        mutated_packet, _ = p.communicate(input=packet)
        mutated_packet = mutated_packet.strip()
        # Calculate the number of mutations performed
        num_mutations = mutated_packet.count(b'MUTATED BY RADAMSA')
        # Generated mutated packet will hold lest than 436 byte of data
        #if len(mutated_packet) <= 6:
        #    break
        #print('\033[92m' + "[+INFO] Mutated Packet: " + '\033[0m', mutated_packet)
        #print('\033[92m' + "[+INFO] Mutated Packet Length: " + '\033[0m', len(mutated_packet))
        return mutated_packet, num_mutations"""


# For arithmetic fuzzing
def arithmetic_mutate(packet, fuzzeable):
    if not fuzzeable:
        return packet, 0
    
    # Convert packet bytes to a list of integers
    nums = [int.from_bytes(packet[i:i+4], byteorder='little', signed=True) for i in range(0, len(packet), 4)]
    
    # Perform arithmetic mutation on each number
    num_mutations = 0
    for i in range(len(nums)):
        if random.randint(0, 99) < mutation_rate:
            # Add a random value to the number
            nums[i] += random.randint(-100, 100)
            num_mutations += 1
    
    # Convert the mutated numbers back to bytes and return
    mutated_packet = b''
    for n in nums:
        mutated_packet += n.to_bytes(4, byteorder='little', signed=True)
 
    return mutated_packet, num_mutations


def sendFuzz(packet, sock, num_mutations):
    MatchString  = b"\x00\x01\x17\xe8"
    CodeSysPacket = b""
    # Check if socket connection is still alive
    if sock.fileno() == -1:
        # Reconnect to the server
        print("Socket broken in SendFuzz! \n")
    else:
        pass

    print('Sending Fuzzed Packet: \n', end='')
    for b in packet:
        print(f'{b:02x}', end=' ')
    print("\n")

    # Send/Receive the fuzzed packet
    sock.send(packet)
    response = sock.recv(1024)

    MatchIndex = response.find(MatchString)

    # If the matching string is not found, return None    
    if MatchIndex == -1:
        CodeSysPacket = b""
    else:
    # Extract the substring from the matching index to the end of the response and return it
        print("Pattern Matched!!\n")
        CodeSysPacket = response[MatchIndex:]    
    
    return CodeSysPacket
