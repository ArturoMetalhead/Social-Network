import json
import time
import socket
import threading
import random
import select
from session_interface import *

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
        self.alive_servers_thread=None

        self.lock = threading.Lock()

        self.stop_threads = False

        self.twitter_server_connected = False

        # Diccionario de sesiones

        self.sessions = {}

        # Lista de servidores de Twitter registrados

        self.registered_twitter_servers = twitter_servers
        self.alive_servers = []


    def start_operator_server(self):

        self.discover_thread = threading.Thread(target=self.discover_operator)
        self.discover_thread.start()

        self.listen_discovery_thread = threading.Thread(target=self.listen_for_discovery)
        self.listen_discovery_thread.start()

        self.alive_servers_thread= threading.Thread(target=self.its_alive_server)
        self.alive_servers_thread.start()

        self.operator.listen()
        print(f"[*] Listening on {self.operator.getsockname()}")

        while not self.stop_threads:

            try:
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
            print(f"Client connected {client_socket.getpeername()} to {self.operator.getsockname()}")

            while not self.stop_threads:

                twitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                with self.lock:

                    print("paso el lock")
                    print(self.alive_servers)
                    
                    for twitter_server in self.alive_servers:

                        print ("entro en for")
                        try:
                            print(f"Trying to connect to Twitter Server: {twitter_server}")

                            twitter_socket.connect(twitter_server)
                            twitter_socket.send(json.dumps({"type": "operator"}).encode())

                            connected=True
                            break
                        except Exception as e:
                            pass


                if not connected:
                    client_socket.send("Not possible to connect to any Twitter Server. Wait a minute please\n".encode())######mandarlo como un tipo warning o algo asi y que el otro lado revise el tipo para poder seguir en eso
                    time.sleep(2)#10
                    continue

                print(f"Connected")####
                #twitter_socket.connect(self.registered_twitter_servers[0])###############################################

                try:

                    ####poner un booleano de si ya tenia una sesion activa y por aqui preguntar si ya estaba iniciada ponerla en home pero con un nuevo twitter socket y hacer un metodo restore

                    session = Session(client_socket,twitter_socket)
                    self.sessions[session] = session

                    session.home()
                except Exception as e:

                    print(f"Error handling session")

                    try:  #####para saber si el que se fue es el cliente o el server de twitter
                        ready_to_read, ready_to_write, in_error = select.select([twitter_socket], [], [], 1.0)
                        if ready_to_read or ready_to_write:
                            print("se jodio el cliente")
                            break
                        else:
                            print("se jodio el server de twitter")
                            connected=False
                            continue
                    except Exception as e:
                        print(e)


        finally:
            if connected:
                self.sessions.pop(session)
            client_socket.close()


    def stop_server(self):
        
        self.stop_threads = True
        self.operator.close()

        for session in self.sessions:
            session.stop()

    # def switch_server(self):

    #     with self.lock:
    #         available_servers = [(ip, port) for ip, port in self.alive_servers if (ip, port) != self.current_server]########cambie lo de registered por alive

    #     if not available_servers:
    #         return False
        
    #     new_server = random.choice(available_servers)
    #     return self.connect_to_server(*new_server) ###### el connect to aqui no tengo
    
    def its_alive_server(self):
        while not self.stop_threads:
            
            with self.lock:
                for twitter_server in self.registered_twitter_servers:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            sock.connect(twitter_server)
                            sock.send(json.dumps({"type": "alive_request"}).encode())
                            response = json.loads(sock.recv(1024).decode())
                            if response["type"] != "alive_response":
                                raise Exception("Invalid response")
                            sock.close()

                            print(f"Server {twitter_server} is alive.")

                            if twitter_server not in self.alive_servers:
                                self.alive_servers.append(twitter_server)
                                print(f"added {twitter_server}")

                    except Exception as e:
                        print(f"Server {twitter_server} is not alive: {e}")

                        try:
                            self.alive_servers.remove(twitter_server)
                            print(f"operator {twitter_server} removed")
                        except ValueError:
                            pass

                        continue

                    
            time.sleep(10)

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

                        #####HABRIA QUE PONER UN CANDADO AQUI PARA QUE NO REGISTRE AL MISMO TIEMPO EN QUE LO UTILICE

                        if (ip, port) not in self.registered_twitter_servers:
                            self.registered_twitter_servers.append((ip, port))
                            #print(f"Discovered Twitter Server: {ip}:{port}")
                            print(f"{self.operator_ip}:{self.operator_port} Discovered Twitter Server: {ip}:{port}")


                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")
    
    #endregion