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
        self.operators=operators
        self.current_server = operators[0]
        self.discover_thread = None
        self.discover_flag=False


    def start_client(self):

        self.client.connect(self.current_server)
        self.client.send(json.dumps({"type": "client"}).encode())

        self.discover_thread = threading.Thread(target=self.discover_operators)
        self.discover_flag=True
        self.discover_thread.start()

        while True:

            #establecer un timer que si pasa de 30 segundos pase a conectarse a otro servidor

            ready = select.select([self.client], [], [], 30)
            if ready[0]:
                try:
                    request = json.loads(self.client.recv(1024).decode())

                    if request['action'] == 'get_operators_request':
                        self.operators = json.loads(request['data'])
                        print("Received operators list.")
                        break
                    else:
                        # Handle other types of requests here
                        print(request["data"])
                        message = input(">> ")
                        message = json.dumps({"action": "message", "data": message})
                        self.client.send(message.encode())
                except json.JSONDecodeError:
                    print("Received invalid JSON data.")
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    if not self.switch_server():
                        print("No available servers to connect. Exiting.")
                        return
            else:
                print("No response from server for 30 seconds. Switching to another server.")
                if not self.switch_server():
                    print("No available servers to connect. Exiting.")
                    return

    def connect_to_server(self, ip, port):
        try:
            self.client.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, port))
            self.current_server = (ip, port)
            self.client.send(json.dumps({"type": "client"}).encode())
            print(f"Connected to server at {ip}:{port}")

            self.discover_flag=True
            self.discover_thread = threading.Thread(target=self.discover_operators)
            return True
        except Exception as e:
            print(f"Failed to connect to {ip}:{port}: {e}")
            return False

    def discover_operators(self):
        while True and self.discover_flag:
            self.client.send(json.dumps({"action": "get_operators"}).encode())
            time.sleep(10)

    def switch_server(self):
        self.discover_flag=False
        self.discover_thread.join()

        available_servers = [(ip, port) for ip, port in self.operators.items() if (ip, port) != self.current_server]
        if not available_servers:
            return False
        
        new_server = random.choice(available_servers)
        return self.connect_to_server(*new_server)
            

    def stop_client(self):
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
