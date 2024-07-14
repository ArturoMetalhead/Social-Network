import socket
import threading
from visual_interface import *
import json
import time


class Server_Manager:
    
    def __init__(self,servers,ip='localhost',port=0):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip,port))
        self.thread_dict={}
        self.registered_servers = servers

    def start_server(self):
        self.server.listen()
        print(f"[*] Listening on {self.server.getsockname()}")

        while True:
            client, addr =self.server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

            request=client.recv(1024).decode()

            if request['type'] == 'server':
                server_handler = threading.Thread(target=self.handle_server, args=(client,))
                server_handler.start()
                self.thread_dict[addr[1]] = server_handler
            
            else:
                client_handler = threading.Thread(target=self.handle_client, args=(client,))
                self.thread_dict[addr[1]] = client_handler
                client_handler.start()

    def handle_client(self,client_socket):

        session = Session(client_socket)
        session.home()

        # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        client_socket.close()

    def discover_servers(self):
        while True:
            for server in self.registered_servers:
                ip, port = server.split(":")
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((ip, port))
                server_socket.send(json.dumps({"action": "register"}).encode())
                server_socket.send(f"{self.server.getsockname()[0]}:{self.server.getsockname()[1]}".encode())
                server_socket.send(json.dumps({"action": "get_server"}).encode())
                server_socket.close
            time.sleep(10)
            

    def handle_server(self,server_socket):####################################
        while True:
            request = server_socket.recv(1024).decode()
            if request['action'] == "get_servers":
                server_socket.send(",".join(self.registered_servers).encode())
            elif request['action'] == "register":
                server_name = server_socket.recv(1024).decode()
                self.registered_servers.append(server_name)
            elif request['action'] == "get_server_request":
                servers_name = request['data']
                for server in servers_name.split(","):
                    if server not in self.registered_servers:
                        self.registered_servers.append(server)
            elif request['action'] == "stop_server":
                self.stop_server()
                break

    def stop_server(self):
        self.server.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()