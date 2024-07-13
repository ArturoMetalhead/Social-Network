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
            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            self.thread_dict[addr[1]] = client_handler
            client_handler.start()

    def handle_client(self,client_socket):
     # Close connection
        self.thread_dict.pop(client_socket.getpeername()[1])
        client_socket.close()

    def stop_server(self):
        self.server.close()
        for key in self.thread_dict:
            self.thread_dict[key].join()

    
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