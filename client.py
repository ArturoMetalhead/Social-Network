import socket
import threading
import os
import json
import time
import random
import select




class Client_Manager:

    def __init__(self,operators,server_master=("localhost",8088)):

        # Socket TCP para conectarse a los servidores

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_server = operators[0]

        # Lista de operadores registrados y los que estan activos

        self.registered_operators=operators
        self.alive_servers=[]
        self.server_master=server_master

        # Hilos en proceso y flag para detenerlos

        self.alive_servers_thread=None
        self.discover_thread = None
        self.discover_flag=False #############para que no se este modificando al mismo tiempo que se examina la lista al cambiar de server
        self.lock=threading.Lock()

        # Configuración de puertos
        id_type_server = 1 #id de operadores
        self.discovery_port = 11000 + id_type_server

        # Diccionario para realizar cache

        self.cache = {}

        # Flag para si el ultimo perfil se ensenno ya al usuario

        self.showed=False ##################


    def start_client(self):

        self.discover_thread = threading.Thread(target=self.listen_for_discovery)
        self.stop_threads = False
        self.discover_flag=True
        self.discover_thread.start()

        self.alive_servers_thread= threading.Thread(target=self.its_alive_server)
        self.alive_servers_thread.start()


        while True: #Para garantizar la conexion inicial


            try:
                self.client.connect(self.current_server)
                self.client.send(json.dumps({"type": "client"}).encode())

                print("ENVIO UN MENSAJE?")
                print(self.current_server)
                break
            
            except Exception as e:
                print(f"Error connecting to server: {e}")
                if not self.switch_server():
                    print("No available servers to connect. Trying in 5 seconds.")
                    time.sleep(5)

                    #preguntar al server master
                    self.ask_server_master()

                    print("SALIO DEL ASK SERVER_MASTER")
                    
                    ###################
                    continue


        while True:

            try:
                incoming_data = self.client.recv(1024).decode()

                try:
                    data = json.loads(incoming_data)
                    if data["action"] == "warning":
                        print(data["data"])
                        continue
                except Exception as e:
                    pass

                # ########## Caching data
                # data = json.loads(incoming_data)
                # if data["action"] == "profile_message":
                #     self.cache[data["username"]] = data["data"]
                #     if self.showed:
                #         print(data["data"])
                #         self.showed=False

                # ##########

                # elif data["action"] == "profile_request":

                #     username=input("@ ")

                #     if data["username"] in self.cache:
                #         print(self.cache[data["username"]])
                #         self.showed=True

                #         response = json.dumps({"action": "profile_response", "data":username})

                # else:

                #########

                    print(incoming_data)

                    not_valid_message=True

                    while not_valid_message:
                        message = input(">> ")
                        if len(message) > 280:
                            print ("Too long message,please try with 280 or less letters")
                        else:
                            not_valid_message=False

                    message = json.dumps({"action": "message", "data": message})
                    self.client.send(message.encode())

            except json.JSONDecodeError:
                print("Received invalid JSON data.")
            except Exception as e:
                print(f"Error receiving data: {e}")
                #print("Va pal switch")########

                while not self.stop_threads:
                    if self.switch_server():
                        print("Switched to another server.")
                        break
                    print("No available servers to connect. Trying in 5 seconds.")

                    #preguntar al server master
                    self.ask_server_master()
                    
                    ###################
                    
                    time.sleep(50)
                    

    def connect_to_server(self, ip, port):
        try:
            self.client.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, port))
            self.current_server = (ip, port)
            self.client.send(json.dumps({"type": "client"}).encode())
            print(f"Connected to server at {ip}:{port}")

            return True
        
        except Exception as e:
            print(f"Failed to connect to {ip}:{port}: {e}")
            return False

    def ask_server_master(self):
        #preguntar al server master
        try:
            print("PREGUNTANDO")
            sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            print("1")
            sock.connect(self.server_master)
            print("2")
            response = json.loads(sock.recv(1024).decode())
            print("3")
            sock.close()

            with self.lock:

                for server in response:
                    if server not in self.registered_operators:
                        print(f"REGISTRO {server}")
                        self.registered_operators.append(server)
            print("RECIBIDO")

        except Exception as e:
                pass

    
    def switch_server(self):

        with self.lock:
            available_servers = [(ip, port) for ip, port in self.alive_servers if (ip, port) != self.current_server]########cambie lo de registered por alive

        if not available_servers:
            return False
        
        new_server = random.choice(available_servers)
        return self.connect_to_server(*new_server)
    


    def listen_for_discovery(self):

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Permite reutilizar la dirección y el puerto
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                sock.bind(('', self.discovery_port))
            except OSError as e:
                print(f"Error binding to discovery port: {e}")
                return

            while not self.stop_threads and self.discover_flag:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())
                    if message['type'] == 'discovery':
                        ip = message['ip']
                        port = message['port']

                        with self.lock:

                            if (ip, port) not in self.registered_operators:
                                self.registered_operators.append((ip, port))
                                #print(f"Discovered operator: {ip}:{port}")
                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")
            

    def stop_client(self):

        self.stop_threads = True
        self.discover_flag=False
        self.discover_thread.join()
        self.discover_thread = None
        self.client.close()

    def its_alive_server(self):

        while not self.stop_threads:
            
            with self.lock:
                for operator in self.registered_operators:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            sock.connect(operator)
                            sock.send(json.dumps({"type": "alive_request"}).encode())
                            response = json.loads(sock.recv(1024).decode())
                            if response["type"] != "alive_response":
                                raise Exception("Invalid response")
                            sock.close()

                            #print(f"Server {operator} is alive.")

                            if operator not in self.alive_servers:
                                self.alive_servers.append(operator)

                    except Exception as e:
                        #print(f"Server {operator} is not alive: {e}")

                        try:
                            self.alive_servers.remove(operator)
                            #print(f"operator {operator} removed")
                        except ValueError:
                            pass
                        continue

            time.sleep(10)