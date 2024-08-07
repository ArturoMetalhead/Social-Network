import socket
import threading
from visual_interface import *
import json
import time


class Server_Manager:
    
    def __init__(self,operators,twitter_servers,ip='localhost',port=0):
        self.operator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.operator.bind((ip,port))
        self.operator_ip=self.operator.getsockname()[0]
        self.operator_port=port
        self.connected={}
        for op in operators:
            self.connected[op]=False


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

            ip=client.getsockname()[0]
            port=client.getsockname()[1]

            if ip==self.operator_ip and port== self.operator_port:
                continue

            print(f"[*] {self.operator_ip}:{self.operator_port} *Accepted connection from {client.getsockname()[0]}:{client.getsockname()[1]}")

            request=client.recv(1024).decode()
            print(request)
            try:
                request=json.loads(request)
                print("request aceptada")

                if request['type'] == 'operator':
                    operator_handler = threading.Thread(target=self.handle_operator, args=(client,))
                    operator_handler.start()
                    self.thread_dict[addr[1]] = operator_handler
                
                elif request['type'] == 'client':
                    client_handler = threading.Thread(target=self.handle_client, args=(client,))
                    self.thread_dict[addr[1]] = client_handler
                    client_handler.start()
            except:
                pass

    def handle_client(self,client_socket):

        session = Session(client_socket)
        self.sessions[client_socket.getpeername()[1]] = session##########


        session.home()

        # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        self.sessions.pop(client_socket.getpeername()[1])##########
        client_socket.close()

    def discover_operators(self):
        while self.discover_flag:
            for operator in self.registered_operators:###########
                if self.connected[operator]!=True:
                    try:
                        self.operator.connect(operator)
                        self.connected[operator]=True
                    except Exception as e:
                        self.connected[operator] = False
                        print(f"Error al conectar con el operador {operator}: {str(e)}")
                

            for operator in self.registered_operators:
                ip, port = operator    #.split(",") ########################## :
                if (self.operator_ip == ip or ip=='localhost' )and self.operator_port == port:
                    continue
                operator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    print("intento conectar operators")
                    print(f"{self.operator_ip}:{self.operator_port} to {ip}:{port}")
                    operator_socket.connect((ip, port))
                    print("conexion exitosa")

                    operator_socket.send(json.dumps({"action": "none","type":"operator"}).encode())
                    print("hice 1")
                    time.sleep(1)
                    operator_socket.send(json.dumps({"action": "register","type":"none","data":(self.operator_ip,self.operator_port)}).encode())
                    print("hice 2")
                    time.sleep(1)
                    operator_socket.send(json.dumps({"action": "get_operators","type":"none"}).encode())
                    print("hice 3")
                    #operator_socket.close

                except:
                    pass

                print(f"[*] Discovered operator at {ip}:{port}")##########

            time.sleep(10)

    def discover_twitter_servers(self):
        while True and self.discover_flag:
            for server in self.registered_twitter_servers:
                ip, port = server   #.split(",")   ####################### :
                twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    twitter_socket.connect((ip, port))
                    twitter_socket.send(json.dumps({"action": "register"}).encode())
                    twitter_socket.send(f"{self.operator.getsockname()[0]}:{self.operator.getsockname()[1]}".encode())
                    twitter_socket.send(json.dumps({"action": "get_twitter_server"}).encode())
                    twitter_socket.close
                except:
                    pass
            time.sleep(10)
            

    def handle_operator(self,operator_socket):####################################
        while True:
            print("handle operator")
            try:
                print("intento")
                request = operator_socket.recv(1024).decode()
                print(request)
                try:
                    print(request)
                    request=json.loads(request)
                    print("valid request")

                    if request['action'] == "get_operators":
                        operators = []
                        for operator in self.registered_operators:
                            operators.append(str(operator))
                        operators_string = ",".join(operators)
                        operator_socket.send(operators_string.encode())
                    elif request['action'] == "register":
                        server_name=request['data']
                        server_name=(server_name[0],server_name[1])
                        if server_name not in self.registered_operators:
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
                except:
                    continue
            except ConnectionResetError:
                print("Connection reset by peer. Reconnecting...")
                connected=False
                for i in range(5):
                    try:
                        operator_ip=operator_socket.getsockname()[0]
                        operator_port=operator_socket.getsockname()[1]
                        operator_socket.close()
                        operator_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        operator_socket.connect((operator_ip, operator_port))
                        connected=True
                    except:
                        pass
                    time.sleep(1)
                if connected:
                    print("Reconnected")
                else:
                    print("Lost connection")
                    break

    def stop_operator(self):
        self.discover_flag=False
        ################################
        self.operator.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()

    def recv_and_send (self,data,client):
        self.sessions[client].recieve_request(data)

