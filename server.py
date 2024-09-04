import json
import time
import socket
import threading
from visual_interface import *

class Operator_Server():
    def __init__(self,twitter_servers=[], ip='localhost', port=0):

        # Configuración de puertos
        id_type_server = 1
        self.discovery_port = 11000 + id_type_server

        # Socket TCP para escuchar conexiones de clientes
        self.operator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.operator.bind((ip, port))
        self.operator_ip = self.operator.getsockname()[0]
        self.operator_port = self.operator.getsockname()[1]

        # Hilos en proceso y flag para detenerlos 

        self.discover_thread = None
        self.listen_discovery_thread = None

        self.stop_threads = False

        self.twitter_server_connected = False

        # Diccionario de sesiones

        self.sessions = {}

        # Lista de servidores de Twitter registrados

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
                    
                    if request['type'] == 'client':
                        client_handler = threading.Thread(target=self.handle_client, args=(client,))
                        client_handler.start()
                        
                    elif request['type'] == 'alive_request':
                        client.send(json.dumps({"type": "alive_response"}).encode())
                        client.close()
                        
                except Exception as e:
                    if not self.stop_threads:
                        print(f"Error handling client: {e}")
                    client.close()
            except socket.timeout:
                continue
            except Exception as e:
                if not self.stop_threads:
                    print(f"Error in main loop: {e}")


    def handle_client(self, client_socket):

        connected=False

        try:
            print(f"Client connected {client_socket.getpeername()} to {self.operator.getsockname()}") ######

            twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            for twitter_server in self.registered_twitter_servers:
                try:
                    print(f"Trying to connect to Twitter Server: {twitter_server}")####
                    twitter_socket.connect(twitter_server)
                    connected=True
                    break
                except Exception as e:
                    pass

            if not connected:
                client_socket.send("Not possible to connect to any Twitter Server. Wait a minute please".encode())
                return

            print(f"Connected")####
            #twitter_socket.connect(self.registered_twitter_servers[0])###############################################

            try:

                session = Session(client_socket,twitter_socket)
                self.sessions[session] = session##########

                session.home()
            except Exception as e:
                print(f"Error handling session")


        finally:
            if connected:
                self.sessions.pop(session)
            client_socket.close()


    def stop_server(self):
        
        self.stop_threads = True
        self.operator.close()

        for session in self.sessions:
            session.stop()

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
                        

                        #####HABRIA QUE PONER UN CANDADO AQUI PARA QUE NO REGISTRE AL MISMO TIEMPO EN QUE LO UTILICE

                        if (ip, port) not in self.registered_twitter_servers:
                            self.registered_twitter_servers.append((ip, port))
                            #print(f"Discovered Twitter Server: {ip}:{port}")
                            print(f"{self.operator_ip}:{self.operator_port} Discovered Twitter Server: {ip}:{port}")


                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")
    
    #endregion