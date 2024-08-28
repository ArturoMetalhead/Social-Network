import os
import socket
import threading
from datetime import datetime
import json
import time

class Twitter_Server():
    def __init__(self,chord_node=None,ip='localhost',port=0):#######


        id_type_server = 2
        self.discovery_port = 11000 + id_type_server

        # Socket TCP para escuchar conexiones de operadores y clientes
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.twitter_server_ip = self.server.getsockname()[0]
        self.twitter_server_port = self.server.getsockname()[1]

        self.discover_thread = None
        self.listen_discovery_thread = None
        self.stop_threads = False
        self.thread_dict={}

        self.chord_node = chord_node

        self.registered_twitter_servers = [] ######No tendria sentido
        self.sessions = {}

    def start_server(self):

        self.server.listen()

        self.discover_thread = threading.Thread(target=self.discover_twitter_servers)
        self.discover_thread.start()

        self.listen_discovery_thread = threading.Thread(target=self.listen_for_discovery)
        self.listen_discovery_thread.start()

        print(f"[*] Listening on {self.server.getsockname()}")

        while not self.stop_threads:
            client, addr =self.server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")


            ######codigo alternativo########
            
            # request=client.recv(1024).decode()
            # request=json.loads(request)

            # print(f"[*] Received request: {request}")

            # if request['type'] == 'operator':
            #     self.sessions[addr[1]] = client
            #     session_handler = threading.Thread(target=self.handle_session, args=(client,))
            #     self.thread_dict[addr[1]] = session_handler
            #     session_handler.start()

            #################################

            self.sessions[addr[1]] = client
            session_handler = threading.Thread(target=self.handle_session, args=(client,))
            self.thread_dict[addr[1]] = session_handler
            session_handler.start()




                

    def handle_session(self, client):

        while not self.stop_threads:
            try:
                request = json.loads(client.recv(1024).decode())
                print(f"[*] Received request: {request}")

                if request['action'] == 'login':
                    username = request['username']
                    password = request['password']
                    #response = self.login(username, password)

                    print("Login")

                    response = 'success'#####################################
                    client.send(json.dumps(response).encode())

                elif request['action'] == 'register':
                    username = request['username']
                    password = request['password']
                    email = request['email']

                    print("Register")

                    response = {
                        'type': 'twitter',
                        'response':'success'
                    }
                    #response = self.register(username, password, email)
                    client.send(json.dumps(response).encode())

                elif request['action'] == 'logout':  ######
                    self.sessions.pop(client.getpeername()[1])
                    client.close()
                    break

            except Exception as e:
                print(f"Error handling session: {e}")
                break




    #region Discovery

    def discover_twitter_servers(self):
        while not self.stop_threads:

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    message = json.dumps({'type': 'discovery','ip':self.twitter_server_ip, 'port': self.twitter_server_port}).encode()
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(message, ('<broadcast>', self.discovery_port))

            except Exception as e:
                print(f"Error sending discovery message: {e}")
            time.sleep(5)

    def listen_for_discovery(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Permite reutilizar la dirección y el puerto
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                sock.bind(('', self.discovery_port))
            except OSError as e:
                print(f"Error binding to discovery port: {e}")
                return

            while not self.stop_threads:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())
                    if message['type'] == 'discovery':
                        ip = message['ip']
                        port = message['port']

                        if (ip, port) not in self.registered_twitter_servers:
                            self.registered_twitter_servers.append((ip, port))
                            print(f"Discovered Twitter server: {ip}:{port}")
                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")
    
    #endregion