import json
import os
from classes import *
from chord.chord import ChordNode
from datetime import datetime
import bcrypt


class Session:
    def __init__(self, client_socket, twitter_socket):
        self.client_socket = client_socket
        self.twitter_socket = twitter_socket ###########################################################
        self.logged_in = False
        self.user = None

    def stop(self):###############3agragar cosas para detener los procesos de por medio

        self.client_socket.send("You are offline".encode())####

        self.client_socket.close()#####
        self.twitter_socket.close()####

    def print_menu(self,options):
        response = ""
        for i, option in enumerate(options, 1):
            response += (f"{i}.{option}\n")
        return response

    def get_user_choice(self,options):
        while True:
            try:
                request = json.loads(self.client_socket.recv(1024).decode())#######################
                #print(self.client_socket.recv(1024).decode())####
                #choice=int(self.client_socket.recv(1024).decode())
                choice=int(request["data"])############

                if 1 <= choice <= len(options):
                    return choice
                else:
                    self.client_socket.send(("Opción inválida. Intente de nuevo.").encode())
            except ValueError:
                self.client_socket.send(("Por favor, ingrese un número válido.").encode())

    def home(self):

        response=("        BIENVENIDO A NUESTRA RED SOCIAL        ")

        if self.logged_in:
            response+= (f"\nBienvenido, {self.user.username}!")
            options = ["Ver perfil", "Ver seguidores", "Ver seguidos", "Publicar", "Cerrar sesión"]
            response+= self.print_menu(options)

            response+= "\nIngrese una opción: "
            self.client_socket.send(response.encode())

            choice = self.get_user_choice(options)
            
            actions = [self.profile, self.followers, self.followings, self.post, self.logout]
            actions[choice - 1]()
        else:
            options = ["Iniciar sesión", "Registrarse"]
            response = self.print_menu(options)

            response+= "\nIngrese una opción: "
            self.client_socket.send(response.encode())
            choice = self.get_user_choice(options)
            
            actions = [self.login, self.register]
            actions[choice - 1]()
        
        self.client_socket.send(("          GRACIAS POR USAR NUESTRA APP    ").encode())

    def send_request(self, request):
        #enviar el socket.getpeername()[1] para saber a quien enviar la respuesta

        try:
            self.twitter_socket.send(json.dumps(request).encode())
            response = self.twitter_socket.recv(1024).decode()
            return json.loads(response)
        
        except Exception as e:
            print(f"Error sending request: {e}")
            return None

    def login(self):
        self.client_socket.send("Ingrese su nombre de usuario: ".encode())
        username= json.loads(self.client_socket.recv(1024).decode())["data"]
        #username = self.client_socket.recv(1024).decode()
        self.verify_back(username) #

        self.client_socket.send("Ingrese su contraseña: ".encode())
        password=json.loads(self.client_socket.recv(1024).decode())["data"]
        #password = self.client_socket.recv(1024).decode()
        self.verify_back(password) #

        request = {
            'type': 'operator',
            'action': 'login',
            'username': username,
            'password': password
        }

        response = self.send_request(request)
        
        if response == 'success':
            self.logged_in = True
            self.client_socket.send(f"Bienvenido nuevamente {username}.".encode())
        
        elif response == "incorrect_password":
            self.client_socket.send("La contraseña es incorrecta".encode())
        else:
            self.client_socket.send("El usuario no existe".encode())
        self.home()
        self.user = User(username, password, " ")

    def register(self):
        succesful_register = False
        while(not succesful_register):
            self.client_socket.send("Ingrese su nombre de usuario: ".encode())
            username = json.loads(self.client_socket.recv(1024).decode())["data"]
            self.verify_back(username) #

            self.client_socket.send("Ingrese su contraseña: ".encode())
            password = json.loads(self.client_socket.recv(1024).decode())["data"]
            self.verify_back(password) #

            self.client_socket.send("Ingrese su correo electrónico: ".encode())
            email = json.loads(self.client_socket.recv(1024).decode())["data"]
            self.verify_back(email) #
            
            # Crear un nuevo usuario con los datos ingresados
            request = {
                'type': 'operator',
                'action': 'register',
                'username': username,
                'password': password,
                'email': email
            }

            response = self.send_request(request)#####response['response'] == 'success'?????? no hay mejor nombre?

            print(response['response'])#####

            if response['response'] == 'success':
                self.logged_in = True
                self.client_socket.send(f"Bienvenido {username}.".encode())
            elif response['response']  == 'user_already_exists':
                self.client_socket.send(f"El nombre de usuario {username} ya existe".encode())
            elif response['response']  == 'password_needed':
                self.client_socket.send("Es necesario que provea una contraseña".encode())
            elif response ['response'] == 'email_needed':
                self.client_socket.send("Es necesario que provea una dirección de email".encode())
        
        # Asignar el usuario a la variable user y cambiar logged_in a True
        self.logged_in = True
        user = User(username, password, email)
        self.user = user

    def display_profile(self, username: str):
        """
        Show user's posts.
        
        :param username: The name of the user whose posts we want to display.
        """
        posts = self.profile(username)
        
        if not posts:
            print(f"El usuario @{username} no tiene publicaciones.")
            return

        print(f"Publicaciones de @{username}:")
        for post in posts:
            if post['type'] == 'tweet':
                print(f"Tweet - {post['created_at']}:")
                print(f"  {post['content']}")
            elif post['type'] == 'retweet':
                print(f"Retweet de @{post['original_user']} - {post['retweeted_at']}:")
                print(f"  (Original creado en {post['created_at']})")
            print("-" * 40)
        

    def logout(self):
        self.logged_in = False
        self.user = None

    def verify_back( self, option ):
        if option == "b":
            self.home()
        else:
            return
        
    def recieve_request(data):##############
        pass