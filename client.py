import socket
import threading
import os
import json



class Client_Manager:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        

    def start_client(self):

        ip = input("Enter IP: ")
        port = int(input("Enter port: "))
        self.client.connect((ip, port))

        ########
        self.client.send(json.dumps({"type": "client"}).encode())

        while True:
            response = self.client.recv(1024)
            print(response.decode())
            message = input(">> ")
            self.client.send(message.encode())
            

    def stop_client(self):
        self.client.close()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    client_manager = Client_Manager()
    client_manager.start_client()
    client_manager.stop_client()
