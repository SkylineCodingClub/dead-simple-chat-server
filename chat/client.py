import message_utils
import socket
import sys
import select

server_address = (sys.argv[1:3])
sock = socket.create_connection(server_address)
message = message_utils.get_next_message(sock)
client_name = message['to']
print "{}: {}".format(message['from'], message['message'])

while True:
    try:
        ready, writer, err = select.select([sock, sys.stdin], [], [], 1000)
        for ready_input in ready:
            if(ready_input == sys.stdin):
                user_input = sys.stdin.readline().rstrip()
                sock.sendall(message_utils.pack({
                    'from': client_name,
                    'message': user_input
                }))
            if(ready_input == sock):
                message = message_utils.get_next_message(sock)
                if(message['from'] != client_name):
                    print "{}: {}".format(message['from'], message['message'])
    except socket.error:
        next
