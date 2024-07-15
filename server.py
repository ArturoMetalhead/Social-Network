import socket
import threading
from visual_interface import *
import json
import time


class Server_Manager:
    
    def __init__(self,operators,twitter_servers,ip='localhost',port=0):
        self.operator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.operator.bind((ip,port))
        self.thread_dict={}


        self.sessions = {}  
        self.registered_twitter_servers = twitter_servers
        self.registered_operators = operators
        
        self.discover_thread = None
        self.discover_flag=False


    def start_operator(self):
        self.operator.listen()
        
        self.discover_flag=True
        twitter_server_discover = threading.Thread(target=self.discover_twitter_servers)
        twitter_server_discover.start()
        operator_discover = threading.Thread(target=self.discover_operators)
        operator_discover.start()
        
        print(f"[*] Listening on {self.operator.getsockname()}")

        while True:
            client, addr =self.operator.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

            request=client.recv(1024).decode()

            if request['type'] == 'operator':
                operator_handler = threading.Thread(target=self.handle_operator, args=(client,))
                operator_handler.start()
                self.thread_dict[addr[1]] = operator_handler
            
            else:
                client_handler = threading.Thread(target=self.handle_client, args=(client,))
                self.thread_dict[addr[1]] = client_handler
                client_handler.start()

    def handle_client(self,client_socket):

        session = Session(client_socket)
        self.sessions[client_socket.getpeername()[1]] = session##########


        session.home()

        # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        self.sessions.pop(client_socket.getpeername()[1])##########
        client_socket.close()

    def discover_operators(self):
        while True and self.discover_flag:
            for operator in self.registered_operators:
                ip, port = operator.split(":")
                operator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                operator_socket.connect((ip, port))
                operator_socket.send(json.dumps({"action": "register"}).encode())
                operator_socket.send(f"{self.operator.getsockname()[0]}:{self.operator.getsockname()[1]}".encode())
                operator_socket.send(json.dumps({"action": "get_server"}).encode())
                operator_socket.close
            time.sleep(10)

    def discover_twitter_servers(self):
        while True and self.discover_flag:
            for server in self.registered_twitter_servers:
                ip, port = server.split(":")
                twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                twitter_socket.connect((ip, port))
                twitter_socket.send(json.dumps({"action": "register"}).encode())
                twitter_socket.send(f"{self.operator.getsockname()[0]}:{self.operator.getsockname()[1]}".encode())
                twitter_socket.send(json.dumps({"action": "get_twitter_server"}).encode())
                twitter_socket.close
            time.sleep(10)
            

    def handle_operator(self,operator_socket):####################################
        while True:
            request = operator_socket.recv(1024).decode()
            if request['action'] == "get_operators":
                operator_socket.send(",".join(self.registered_operators).encode())
            elif request['action'] == "register":
                server_name = operator_socket.recv(1024).decode()
                self.registered_operators.append(server_name)
            elif request['action'] == "get_operators_request":
                operators_name = request['data']
                for operator in operators_name.split(","):
                    if operator not in self.registered_operators:
                        self.registered_operators.append(operator)
            elif request['action'] == "stop_server":
                self.stop_operator()
                break

            elif request['action'] == "get_twitter_server":
                operator_socket.send(",".join(self.registered_twitter_servers).encode())
            elif request['action'] == "register_twitter_server":####################################
                server_name = operator_socket.recv(1024).decode()
                self.registered_twitter_servers.append(server_name)

            elif request['action'] == "send2client":
                self.recv_and_send(request['data'],request['objetive'])

    def stop_operator(self):
        self.discover_flag=False
        ################################
        self.operator.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()

    def recv_and_send (self,data,client):
        self.sessions[client].recieve_request(data)

