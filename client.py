import socket
import threading
import os
import json
import time
import random
import select




class Client_Manager:
    def __init__(self,operators):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.registered_operators=operators
        self.current_server = operators[0]
        self.discover_thread = None ############
        self.discover_flag=False #############para que no se este modificando al mismo tiempo que se examina la lista al cambiar de server
        self.lock=threading.Lock()####

        ###########

        # Configuración de puertos
        id_type_server = 1 #id de operadores
        #ID = 1
        # PORT_LISTEN = 11000 + id_type_server
        # PORT_BR = 12000 + id_type_server

        self.discovery_port = 11000 + id_type_server


    def start_client(self):

        self.client.connect(self.current_server)
        self.client.send(json.dumps({"type": "client"}).encode())

        self.discover_thread = threading.Thread(target=self.listen_for_discovery)
        self.stop_threads = False
        self.discover_flag=True
        self.discover_thread.start()

        while True:

            #establecer un timer que si pasa de 30 segundos pase a conectarse a otro servidor

            #ready = select.select([self.client], [], [], 30)######??????
            #if ready[0]:
                try:
                    print(self.client.recv(1024).decode())#####
                    #request = json.loads(self.client.recv(1024).decode())

                    # Handle other types of requests here
                    #print(request["data"])
                    message = input(">> ")
                    message = json.dumps({"action": "message", "data": message})
                    self.client.send(message.encode())

                except json.JSONDecodeError:
                    print("Received invalid JSON data.")
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    print("Va pal switch")########

                    while not self.stop_threads:
                        if self.switch_server():
                            print("Switched to another server.")
                            break
                        print("No available servers to connect. Trying in 5 seconds.") ################AQUI DEBO PONERLE PARA QUE ESPERE A QUE HAYA NUEVOS A LOS QUE CONECTARSE EN VEZ DE DEJARLO EN El AIRE
                        
                        time.sleep(50)
                    

    def connect_to_server(self, ip, port):###ip separado de port?
        try:
            self.client.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, port))
            self.current_server = (ip, port)
            self.client.send(json.dumps({"type": "client"}).encode())
            print(f"Connected to server at {ip}:{port}")

            # self.discover_flag=True
            # self.discover_thread = threading.Thread(target=self.listen_for_discovery)
            # self.discover_thread.start()

            return True
        
        except Exception as e:
            print(f"Failed to connect to {ip}:{port}: {e}")
            return False

    
    def switch_server(self):

        # lock = threading.Lock()

        print ("A")########
        # self.discover_flag=False
        # self.discover_thread.join()
        print ("B")########

        with self.lock:##############################################
            available_servers = [(ip, port) for ip, port in self.registered_operators if (ip, port) != self.current_server]

        if not available_servers:
            print("C")########
            # self.discover_flag=True#########
            # self.discover_thread = threading.Thread(target=self.listen_for_discovery)#######
            # self.discover_thread.start()########
            print("D")########
            return False
        
        new_server = random.choice(available_servers)  ########TENGO QUE PONER PARA ELIMINAR LOS QUE NO ESTAN VIVOS
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

                        with self.lock:##########################################################

                            if (ip, port) not in self.registered_operators:
                                self.registered_operators.append((ip, port))
                                print(f"Discovered operator: {ip}:{port}")
                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")

            print("paro el listen for discovery")########
            

    def stop_client(self):
        self.stop_threads = True
        self.discover_flag=False
        self.discover_thread.join()
        self.discover_thread = None
        self.client.close()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    client_manager = Client_Manager()
    client_manager.start_client()
    client_manager.stop_client()