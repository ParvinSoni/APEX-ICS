import zlib


def crc32_checksum(value):

    checksum = zlib.crc32(value)
    size = len(value)
    payload_size = int(size)

    # convert the checksum to bytes in little endian format
    checksum_bytes = checksum.to_bytes(4, byteorder='little')
    checksum_len = payload_size.to_bytes(4, byteorder='little')

    # Adding Service Layer + CRC32
    final_checksum = checksum_len + checksum_bytes
    return(final_checksum)