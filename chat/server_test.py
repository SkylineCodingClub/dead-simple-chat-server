import socket
import re
import time
import message_utils
from nose.tools import assert_raises

socket.setdefaulttimeout(10)
server_address = ('localhost', 10000)


#server should accept incoming connections
def connection_test():
    sock = socket.create_connection(server_address)
    message = message_utils.get_next_message(sock)
    sock.close()
    print message['message']
    assert re.match(u"welcome to the server \w+", message['message'])


#server should accept 100 concurrent connections
def multi_connction_test():
    connections = []
    for i in range(1, 10):
        sock = socket.create_connection(server_address)
        connections.append(sock)

    for sock in connections:
        try:
            message = message_utils.get_next_message(sock)
        except socket.error:
            assert False == "Raised socket exception"
        assert re.match(u"welcome to the server \w+", message['message'])

    for sock in connections:
        assert sock.send(u"so glad to be here") != 0
        sock.close()


def flood_connction_test():
    assert_raises(socket.error, socket_flood, server_address)


def socket_flood(server_address):
    connections = []
    for i in range(1, 2000):
        sock = socket.create_connection(server_address)
        connections.append(sock)

    for sock in connections:
        assert sock.send(u"so glad to be here") != 0
        sock.close()


def flapping_user_test():
    server_address = ('localhost', 10000)
    for i in range(1, 2):
        connections = []
        for i in range(1, 2000):
            try:
                sock = socket.create_connection(server_address)
            except socket.error:
                assert False == "Bad socket created"

            sock.close()

        for i in range(1, 10):
            try:
                sock = socket.create_connection(server_address)
            except socket.error:
                assert False == "Bad socket created"
            connections.append(sock)

        for sock in connections:
            print sock.fileno()
            assert sock.send(u"so glad to be here") != 0
            sock.close()


def bad_message_test():
    server_address = ('localhost', 10000)
    sock = socket.create_connection(server_address)
    message = message_utils.get_next_message(sock)
    assert re.match(u"welcome to the server \w+", message['message'])
    assert sock.send(u"so glad to be here") != 0
    time.sleep(2)
    sock.settimeout(2)
    try:
        assert len(sock.recv(1)) == 0
    except:
        assert False == "Socket returned data"


def good_message_test():
    server_address = ('localhost', 10000)
    sock = socket.create_connection(server_address)
    message = message_utils.get_next_message(sock)
    assert re.match(u"welcome to the server \w+", message['message'])
    print message
    to_send = {
        'from': message['to'],
        'to': message['to'],
        'message': "This is a test message"
    }
    assert sock.sendall(message_utils.pack(to_send)) is None
    new_message = message_utils.get_next_message(sock)
    print new_message
    assert re.match(u"This is a test message", new_message['message'])


def broadcast_test():
    server_address = ('localhost', 10000)
    connections = {}
    sender = ""
    for i in range(1, 3):
        sock = socket.create_connection(server_address)
        message = message_utils.get_next_message(sock)
        assert re.match(u"welcome to the server \w+", message['message'])
        sender = message['to']
        connections[sender] = sock

    assert connections[sender].sendall(message_utils.pack({
        'from': sender,
        'message': "Broadcast message"
    })) is None

    for sock in connections.values():
        message = message_utils.get_next_message(sock)
        assert re.match(u"Broadcast message", message['message'])


#server should relay message data between clients
