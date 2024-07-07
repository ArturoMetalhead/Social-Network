import socket
import threading


class Server_Manager:
     
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((' ',0))
        self.thread_dict={}

    def start_server(self):
        self.server.listen()
        print(f"[*] Listening on {self.server.getsockname()}")

        while True:
            client, addr =self.server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            self.thread_dict[addr[1]] = client_handler
            client_handler.start()

    def handle_client(self,client_socket):
        request = client_socket.recv(1024)
        print(f"[*] Received: {request}")
        client_socket.send(b"ACK!")


        # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        client_socket.close()

    def stop_server(self):
        self.server.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()