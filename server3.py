import json
import time
import socket
import threading
from visual_interface import *

class Operator_Server():
    def __init__(self, operators=[], twitter_servers=[], ip='localhost', port=0):

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

        operators.append((ip, port)) # Agregar el propio servidor a la lista de operadores
        self.registered_operators = operators
        #self.registered_operators_connected = {op: False for op in self.registered_operators}


    def start_operator_server(self):

        self.discover_thread = threading.Thread(target=self.discover_operators)
        self.discover_thread.start()

        self.listen_discovery_thread = threading.Thread(target=self.listen_for_discovery)
        self.listen_discovery_thread.start()
        
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

            session = Session(client_socket)
            #self.sessions[client_socket.getpeername()[1]] = session##########

            session.home()

            # Close connection
            # self.thread_dict.pop(client_socket.getpeername()[1])
            # self.sessions.pop(client_socket.getpeername()[1])##########
        finally:
            client_socket.close()


    def discover_operators(self):
        while not self.stop_threads:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    message = json.dumps({'type': 'discovery','ip':self.operator_ip, 'port': self.operator_port}).encode()
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(message, ('<broadcast>', self.discovery_port))

            except Exception as e:
                print(f"Error sending discovery message: {e}")
            time.sleep(5)


    # def listen_for_discovery(self):  ######deberia hacer un hilo con cada solicitud de operador
    #     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    #         sock.bind(('', self.discovery_port))

    #         while not self.stop_threads:

    #             data, addr = sock.recvfrom(1024)
    #             message = json.loads(data.decode())
    #             if message['type'] == 'discovery':

    #                 ip= message['ip']
    #                 port = message['port']

    #                 if (ip, port) not in self.registered_operators:
    #                     self.registered_operators.append((ip, port))
    #                     print(f"Discovered operator: {ip}:{port}")

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

                        if (ip, port) not in self.registered_operators:
                            self.registered_operators.append((ip, port))
                            print(f"Discovered operator: {ip}:{port}")
                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")
