import socket
import threading
import json



class Server_Master():
    def __init__(self,ip='localhost',port=0,id_type_server=0):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_ip = self.server_socket.getsockname()[0]
        self.server_port = self.server_socket.getsockname()[1]

        self.id_type_server = id_type_server
        self.discovery_port = 11000 + id_type_server

        self.servers=[]

        self.stop_threads = False
        self.thread_dict={}
        self.listen_discovery_thread = None


    def start_server(self):

        self.listen_discovery_thread = threading.Thread(target=self.listen_for_discovery)
        self.listen_discovery_thread.start()

        self.server_socket.listen()
        print(f"[*] Listening on {self.server_socket.getsockname()}")

        while not self.stop_threads:
            try:
                client, addr = self.server_socket.accept()
                print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

                client_handler = threading.Thread(target=self.handle_client, args=(client,))
                client_handler.start()

            except Exception as e:
                if not self.stop_threads:
                    print(f"Error in main loop: {e}")
                client.close()


    def handle_client(self,client):

        print("ALGUIEN SE CONECTO")

        while not self.stop_threads:
            try:
                client.send(json.dumps(self.servers).encode())
                print("SE ENVIO")

            finally:
                client.close()
                break
            

    def stop_server(self):
        self.stop_threads = True
        self.server_socket.close()
        self.listen_discovery_thread.join()


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

                        if (ip, port) not in self.servers:
                            self.servers.append((ip, port))
                            print(f"Server Master {self.id_type_server} {self.server_ip}:{self.server_port} Discovered Server: {ip}:{port}")


                except Exception as e:
                    print(f"Error in listen_for_discovery: {e}")