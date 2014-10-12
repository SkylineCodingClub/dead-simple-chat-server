import socket
import random
import os
import select
import message_utils


class ChatServer:
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connections = {}
        self.address = address
        self.port = port

    def start(self):
        self.socket.bind((self.address, self.port))
        self.socket.listen(100)
        
        filename = os.path.dirname(__file__)+"/data/names"
        self.names = self.load_name_list(filename)

        while True:
            readers = [x for x in self.connections.values() if x != 0]
            readers.append(self.socket)
            read_ready, write_ready, in_error = \
                select.select(readers, [], [], 1000)

            for sock in read_ready:
                if(sock == self.socket):
                    connection, client_address = self.socket.accept()
                    connection.settimeout(2)
                    try:
                        username = self.reserve_user(client_address)
                        self.connections[client_address] = connection
                        self.send_message(self.welcome_message(username))
                    except MaxConnections:
                        connection.close()
                        next
                else:
                    try:
                        message = message_utils.get_next_message(sock)
                        if(self.validate(message, sock)):
                            self.send_message(message)
                    except socket.error:
                        self.remove_user(self.socket_to_user(sock))
                        sock.close()

            for sock in in_error:
                self.remove_user(self.socket_to_user(sock))
                sock.close()

    def load_name_list(self, filename):
        file_handle = open(filename, 'r+')
        name_list = file_handle.read()
        return dict((a, 0) for a in name_list.split("\n"))

    def welcome_message(self, username):
        return {
            "message": "welcome to the server {0}".format(username),
            "from": "server",
            "to": username,
        }

    def reserve_user(self, client):
        available = [name for name in self.names if self.names[name] == 0]
        selection = available[random.randint(0, len(available) - 1)]
        if(not selection):
            raise MaxConnections("no more names available")
        self.names[selection] = client
        return selection

    def user_to_socket(self, username):
        client_address = self.names[username]
        if(not client_address):
            raise BadUserName("No client address associated with {0}".format(
                username
            ))

        socket = self.connections[client_address]
        if(not socket):
            raise BadUserName(("No socket associated with "
                               "client address {0}").format(
                client_address
            ))

        return socket

    def socket_to_user(self, sock):
        clients = [client for client in self.connections
                   if self.connections[client] == sock]
        if(not clients):
            return

        client_address = clients.pop()
        users = [user for user in self.names
                 if self.names[user] == client_address]

        if(not users):
            return

        username = users.pop()
        return username

    def send_message(self, message):
        packed_message = message_utils.pack(message)

        if('to' not in message):
            message['to'] = 'all'

        if(message['to'] == 'all'):
            for sock in self.connections.values():
                if(sock):
                    sock.sendall(packed_message)
        else:
            try:
                sock = self.user_to_socket(message['to'])
                sock.sendall(packed_message)
            except socket.error:
                self.remove_user(message['to'])

    def validate(self, message, sock):
        if(isinstance(message, dict)):
            if(message['from'] and message['message']):
                if(self.socket_to_user(sock) == message['from']):
                    return True
        return False

    def remove_user(self, user):
        if(not user):
            return
        to_remove = self.connections[self.names[user]]
        self.connections[self.names[user]] = 0
        self.names[user] = 0
        if(to_remove == 0):
            # already removed
            return
        to_remove.close()


class BadUserName(Exception):
    def __init__(self, message):
        super(BadUserName, self).__init__(message)


class MaxConnections(Exception):
    def __init__(self, message):
        super(MaxConnections, self).__init__(message)
