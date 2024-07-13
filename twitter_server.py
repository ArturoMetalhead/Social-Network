import os
import socket
import threading
from datetime import datetime

class Twitter_Server():
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost',0))
        self.thread_dict={}
        self.chord_node = None

    def start_server(self):
        self.server.listen()
        print(f"[*] Listening on {self.server.getsockname()}")

        while True:
            client, addr =self.server.accept()
            print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            session_handler = threading.Thread(target=self.handle_session, args=(client,))
            self.thread_dict[addr[1]] = session_handler
            session_handler.start()

    def handle_session(self,client_socket):
        while(True):
            request = client_socket.recv(1024).decode()
            if(request['action'] == 'login'):
                response = self.login(request['username'], request['password'])
            
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
            client_socket.send(response.encode())


     # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        client_socket.close()

    def stop_server(self):
        self.server.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()
        
    def login(self,username, password):
        # Verify if user exists in database
        if self.user_exists(username):
            # Verify if password is correct
            if self.verify_password(username, password):
                return "success"
            else:
                return "incorrect_password"
        else:
            return "user_not_found"

    def user_exists(self, username):
        # Check if user exists in the database
        # Implement your logic here
        return False

    def verify_password(self, username, password):
        # Verify if the password is correct for the given username
        # Implement your logic here
        return False

    def profile(self):
        user_tweets = self.local_node.retrieve_data(self.user.username, "tweets") ########################################
        user_retweets = self.local_node.retrieve_data(self.user.username, "retweets")
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