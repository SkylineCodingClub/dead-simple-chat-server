import json
import struct
import socket
import sys


def pack(message):
    encoded_message = json.dumps(message)
    message_size = len(encoded_message)
    return struct.pack('!L' + str(message_size) + 's',
                       message_size, encoded_message)


def get_next_message(sock):
    packed_size = ""
    while(len(packed_size) < 4):
        packed_size = packed_size + sock.recv(4 - len(packed_size))
        if(not packed_size):
            raise socket.error

    if(packed_size == "/ HT"):
        sys.stderr.write("YEY HTTP\n")
    size = struct.unpack("!L", packed_size)[0]
    received_size = 0
    packed_message = ""
    sock.settimeout(3)
    while(received_size < size):
        next_chunk = sock.recv(size - received_size)
        if(len(next_chunk) == 0):
            raise socket.error
        received_size = len(next_chunk)
        packed_message = packed_message + next_chunk
        sys.stderr.write(packed_message)
    encoded_message = struct.unpack("!" + str(size) + "s", packed_message)[0]
    message = json.loads(encoded_message)
    return message
