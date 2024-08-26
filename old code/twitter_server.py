import os
import socket
import threading
from datetime import datetime
import json
import time

class Twitter_Server():
    def __init__(self, twitter_servers,chord_node,ip='localhost',port=0):#######
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip,port))
        self.thread_dict={}
        self.chord_node = chord_node
        self.dicover_flag=False
        self.discover_thread=None
        self.registered_twitter_servers = twitter_servers
        self.sessions = {}

    def start_server(self):
        self.server.listen()

        self.dicover_flag=True
        self.discover_thread = threading.Thread(target=self.discover_twitter_servers)

        print(f"[*] Listening on {self.server.getsockname()}")

        while True:
            client, addr =self.server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            
            request=client.recv(1024).decode()

            if request['type'] == 'twitter_server':
                server_handler = threading.Thread(target=self.handle_server, args=(client,))
                server_handler.start()
                self.thread_dict[addr[1]] = server_handler

            else:
                self.sessions[addr[1]] = client
                session_handler = threading.Thread(target=self.handle_session, args=(client,))
                self.thread_dict[addr[1]] = session_handler
                session_handler.start()


    def handle_session(self,client_socket): #aqui hago lo que el cliente le dijo al server que hiciera
        while(True):
            request = client_socket.recv(1024).decode()
            if(request['action'] == 'login'):
                response = self.login(request['data'])

            elif(request['action'] == 'register'):
                response =  self.register(request['data'])
            
            elif(request['action'] == 'profile'):
                response = self.profile()
            
            elif(request['action'] == 'followings'):
                response = self.followings()
            
            elif(request['action'] == 'followers'):
                response = self.followers()
            
            elif(request['action'] == 'post'):
                response = self.post(request['content'])
            
            elif(request['action'] == 'stop_server'):
                self.stop_server()
                break

            request={"data":response,"action":'send2client',"objetive":client_socket.getpeername()[1]} ####ahora no se si esto va en comillas simples o dobles

            request=json.dumps(request).encode()

            client_socket.send(request) #enviandoselo al servidor para que se lo de al cliente objetivo


     # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        client_socket.close()

    def discover_twitter_servers(self):
        while True and self.dicover_flag:
            for server in self.registered_twitter_servers:
                ip, port = server.split(":")
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((ip, port))
                server_socket.send(json.dumps({"action": "register"}).encode())
                server_socket.send(f"{self.server.getsockname()[0]}:{self.server.getsockname()[1]}".encode())
                server_socket.send(json.dumps({"action": "get_twitter_server"}).encode())
                server_socket.close
            time.sleep(10)


    def handle_server(self,server_socket):

        #Extract server's ip and port
        ip=server_socket.getpeername()[0]
        port=server_socket.getpeername()[1]

        if f"{ip}:{port}" not in self.registered_twitter_servers:
            self.registered_twitter_servers.append(f"{ip}:{port}")

        while True:
            request = server_socket.recv(1024).decode()
            if request['action'] == "get_twitter_server":
                message=json.dumps({"action": "get_twitter_server_request","data":",".join(self.registered_twitter_servers)}).encode()
                server_socket.send(message)
            elif request['action'] == "register":
                server_name = server_socket.recv(1024).decode()
                self.registered_twitter_servers.append(server_name)
            elif request['action'] == "get_twitter_server_request":
                servers_name = request['data']
                for server in servers_name.split(","):
                    if server not in self.registered_twitter_servers:
                        self.registered_twitter_servers.append(server)
            elif request['action'] == "stop_server":
                self.stop_server()
                break
            elif request['action'] == "send2client":
                self.recv_and_send(request,request['objetive'])


    def recv_and_send(self,request,objetive):
        client_socket=self.sessions[objetive]
        client_socket.send(request.encode())
            

    def stop_server(self):
        self.dicover_flag=False
        self.server.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()
        
    def login(self, data):
        username = data['username']
        password = data['password']
        # Verify if user exists in database
        if self.user_exists(username):
            # Verify if password is correct
            if self.verify_password(username, password):
                return 'success'
            else:
                return 'incorrect_password'
        else:
            return 'user_not_found'
        
    def register(self, data):
        username = data['username']
        if self.user_exists(username):
            return 'user_already_exists'
        
        password = data['password']
        if not password:
            return 'password_needed'
        
        email = data['email']
        if not email:
            return 'email_needed'
        
        user = {
            'username': username,
            'password': password,
            'email': email
        }

        self.local_node.store_data(username, user)
        return 'success'


    def user_exists(self, username):
        return self.local_node.verify_user(username)

    def verify_password(self, username, password):
        return self.local_node.verify_password(username, password)

    def profile(self, prof_username):
        user_tweets = self.local_node.retrieve_data(prof_username, "tweets") ########################################
        user_retweets = self.local_node.retrieve_data(prof_username, "retweets")
        posts = []
        posts.extend(user_tweets)
        posts.extend(user_retweets)
        
        # Sorted by date created (recents first)
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        return posts
    
    def followings(self):
        user_followings = self.local_node.retrieve_data(self.user.username, "following")
        return user_followings

    def followers(self):
        user_followers = self.local_node.retrieve_data(self.user.username, "folllowers")
        return user_followers

    def post(self, content):
        # Add a verif. for amount of characters
        tweet = {
            'user': self.user,
            'content': content,
            'created_at':datetime.now()
        } ############################################# We need to verify if it takes this like an instance of Tweet

        self.local_node.store_data(self.user.username, tweet)

        # we need to notify the user if the tweet was posted correctly