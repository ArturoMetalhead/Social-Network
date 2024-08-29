import json
import time
import socket
import threading
from visual_interface import *

class Operator_Server():
    def __init__(self,twitter_servers=[], ip='localhost', port=0):

        # Configuración de puertos
        id_type_server = 1
        #ID = 1
        # PORT_LISTEN = 11000 + id_type_server
        # PORT_BR = 12000 + id_type_server

        self.discovery_port = 11000 + id_type_server

        # Socket TCP para escuchar conexiones de operadores y clientes
        self.operator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.operator.bind((ip, port))
        self.operator_ip = self.operator.getsockname()[0]
        self.operator_port = self.operator.getsockname()[1]

        # Socket UDP para descubrimiento

        self.discover_thread = None
        self.listen_discovery_thread = None
        self.stop_threads = False

        self.twitter_server_connected = False
        #self.twitter_server_socket = None###############################################

        self.registered_twitter_servers = twitter_servers


    def start_operator_server(self):

        self.discover_thread = threading.Thread(target=self.discover_operator)
        self.discover_thread.start()

        self.listen_discovery_thread = threading.Thread(target=self.listen_for_discovery)
        self.listen_discovery_thread.start()

        #while not self.twitter_server_connected:
        
        self.operator.listen()
        print(f"[*] Listening on {self.operator.getsockname()}")

        while not self.stop_threads:
            try:
                self.operator.settimeout(1.0)
                client, addr = self.operator.accept()
                try:
                    request = client.recv(1024).decode()
                    request = json.loads(request)
                    
                    if request['type'] == 'operator':#############
                        operator_handler = threading.Thread(target=self.handle_operator, args=(client,))
                        operator_handler.start()
                    elif request['type'] == 'client':
                        client_handler = threading.Thread(target=self.handle_client, args=(client,))
                        client_handler.start()
                except Exception as e:
                    print(f"Error handling client: {e}")
                    client.close()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in main loop: {e}")


    ########################################################No tendria sentido
    def handle_operator(self, client):
        try:
            message = json.dumps({'type': 'operator_request', 'data': self.registered_operators}).encode()
            client.send(message)
            print(f"Sending operator_request to {client.getpeername()}")

        except Exception as e:
            print(f"Error sending operator_request to {client.getpeername()}: {e}")

    ######################################################

    def handle_client(self, client_socket):
        try:
            print(f"Client connected {client_socket.getpeername()} to {self.operator.getsockname()}")

            twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to Twitter Server: {self.registered_twitter_servers[0]}")####
            twitter_socket.connect(self.registered_twitter_servers[0])###############################################

            session = Session(client_socket,twitter_socket)####VOY A TENER QUE USAR VARIOS TWITTERSOCKET PARA QUE NO SE HAGA UN CUELLO DE BOTELLA
            #self.sessions[client_socket.getpeername()[1]] = session##########

            session.home()

            # Close connection
            # self.thread_dict.pop(client_socket.getpeername()[1])
            # self.sessions.pop(client_socket.getpeername()[1])##########
        finally:
            client_socket.close()

    #region Discovery

    def discover_operator(self):
        while not self.stop_threads:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    message = json.dumps({'type': 'discovery','ip':self.operator_ip, 'port': self.operator_port}).encode()
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
                sock.bind(('', self.discovery_port+1))##############
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




                        ################################

                        # print(f"{self.operator_ip}:{self.operator_port} {self.registered_twitter_servers}")
                        # if(self.operator_port == 8081):
                        #     continue


                        if (ip, port) not in self.registered_twitter_servers:
                            self.registered_twitter_servers.append((ip, port))
                            #print(f"Discovered Twitter Server: {ip}:{port}")
                            print(f"{self.operator_ip}:{self.operator_port} Discovered Twitter Server: {ip}:{port}")


                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")
    
    #endregion