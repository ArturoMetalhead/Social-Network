
#region old

# logged_in = False
# user = None


# def home():
#     if logged_in:
#         print("Bienvenido, ", user.username)
#         print ("1. Ver perfil")
#         print ("2. Ver seguidores")
#         print ("3. Ver seguidos")
#         print ("4. Publicar")
#         print ("5. Cerrar sesión")
#         option = input("Ingrese una opción: ")
#         if option == "1":
#             profile()
#         elif option == "2":
#             followers()
#         elif option == "3":
#             followings()
#         elif option == "4":
#             post()
#         elif option == "5":
#             logout()
#         else:
#             print("Opción inválida")
#     else:
#         print("1. Iniciar sesión")
#         print("2. Registrarse")
#         option = input("Ingrese una opción: ")
#         if option == "1":
#             login()
#         elif option == "2":
#             register()
#         else:
#             print("Opción inválida")

# def login():
    
#     global logged_in
#     global user
#     username = input("Ingrese su nombre de usuario: ")
#     password = input("Ingrese su contraseña: ")

#     ###########################################################################################
#     # Verificar si el usuario y contraseña son correctos
#     # Si son correctos, asignar el usuario a la variable user y cambiar logged_in a True
#     # Si no son correctos, imprimir un mensaje de error

#     logged_in = True
#     user = User(username, password, " ") #######

# def register():
    
#     global logged_in
#     global user
#     username = input("Ingrese su nombre de usuario: ")
#     password = input("Ingrese su contraseña: ")
#     email = input("Ingrese su correo electrónico: ")

#     ###########################################################################################
#     # Crear un nuevo usuario con los datos ingresados
#     # Asignar el usuario a la variable user y cambiar logged_in a True

#     logged_in = True
#     user = User(username, password, email) ########

# def profile():
#     ##################################
#     # Extraer publicaciones hechas por el usuario

#     pass


# def followings():
    
#     ##################################
#     # Extraer usuarios seguidos por el usuario

#     pass

# def followers():
    
#     ##################################
#     # Extraer seguidores del usuario

#     pass

# def post():
#     ##################################
#     # Crear una nueva publicación

#     pass

# def logout():
    
#     global logged_in
#     global user
#     logged_in = False
#     user = None

#     home()

# endregion

########################################################################

# import os
# from colorama import init, Fore, Back, Style

# init(autoreset=True)

# logged_in = False
# user = None

# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

# def print_header():
#     print(Fore.CYAN + "=" * 50)
#     print(Fore.YELLOW + "        BIENVENIDO A NUESTRA RED SOCIAL        ")
#     print(Fore.CYAN + "=" * 50)

# def print_footer():
#     print(Fore.CYAN + "=" * 50)
#     print(Fore.YELLOW + "          GRACIAS POR USAR NUESTRA APP    ")
#     print(Fore.CYAN + "=" * 50)

# def print_menu(options):
#     for i, option in enumerate(options, 1):
#         print(f"{Fore.GREEN}{i}. {Fore.WHITE}{option}")

# def get_user_choice(options):
#     while True:
#         try:
#             choice = int(input(Fore.YELLOW + "\nIngrese una opción: "))
#             if 1 <= choice <= len(options):
#                 return choice
#             else:
#                 print(Fore.RED + "Opción inválida. Intente de nuevo.")
#         except ValueError:
#             print(Fore.RED + "Por favor, ingrese un número válido.")

# def home():
#     clear_screen()
#     print_header()
    
#     if logged_in:
#         print(Fore.CYAN + f"\nBienvenido, {user.username}!")
#         options = ["Ver perfil", "Ver seguidores", "Ver seguidos", "Publicar", "Cerrar sesión"]
#         print_menu(options)
#         choice = get_user_choice(options)
        
#         actions = [profile, followers, followings, post, logout]
#         actions[choice - 1]()
#     else:
#         options = ["Iniciar sesión", "Registrarse"]
#         print_menu(options)
#         choice = get_user_choice(options)
        
#         actions = [login, register]
#         actions[choice - 1]()
    
#     print_footer()


# def login():
#     global logged_in
#     global user
#     username = input(Fore.YELLOW + "Ingrese su nombre de usuario: ")
#     verify_back(username) #
#     password = input("Ingrese su contraseña: ")
#     verify_back(password) #
    
#     # Verificar si el usuario y contraseña son correctos
#     # Si son correctos, asignar el usuario a la variable user y cambiar logged_in a True
#     # Si no son correctos, imprimir un mensaje de error

#     if verify_user(username, password):
#         logged_in = True

#     #user = User(username, password, " ")

# def register():
#     global logged_in
#     global user
#     username = input(Fore.YELLOW + "Ingrese su nombre de usuario: ")
#     verify_back(username) #
#     password = input("Ingrese su contraseña: ")
#     verify_back(password) #
#     email = input("Ingrese su correo electrónico: ")
#     verify_back(email) #
    
#     # Crear un nuevo usuario con los datos ingresados
#     # Asignar el usuario a la variable user y cambiar logged_in a True
#     logged_in = True
#     #user = User(username, password, email)

# def profile():
#     # Extraer publicaciones hechas por el usuario
#     pass

# def followings():
#     # Extraer usuarios seguidos por el usuario
#     pass

# def followers():
#     # Extraer seguidores del usuario
#     pass

# def post():
#     # Crear una nueva publicación
#     pass

# def logout():
#     global logged_in
#     global user
#     logged_in = False
#     user = None

# def verify_back( option ):
#     if option == "b":
#         home()
#     else:
#         return



# if __name__ == "__main__":
#     while True:
#         home()




###############################################NEW VERSION WEB

import os
from classes import *
from chord.chord import ChordNode
from datetime import datetime


class Session:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.logged_in = False
        self.user = None

    def print_menu(self,options):
        response = ""
        for i, option in enumerate(options, 1):
            response += (f"{i}.{option}\n")
        return response

    def get_user_choice(self,options):
        while True:
            try:
                choice=int(self.client_socket.recv(1024).decode())
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

    def login(self):


        self.client_socket.send("Ingrese su nombre de usuario: ".encode())
        username = self.client_socket.recv(1024).decode()
        self.verify_back(username) #
        self.client_socket.send("Ingrese su contraseña: ".encode())
        password = self.client_socket.recv(1024).decode()
        self.verify_back(password) #
        
        # Verificar si el usuario y contraseña son correctos
        # Si son correctos, asignar el usuario a la variable user y cambiar logged_in a True
        # Si no son correctos, imprimir un mensaje de error

        if self.verify_user(username, password):
            self.logged_in = True

        #user = User(username, password, " ")

    def register(self):

        self.client_socket.send("Ingrese su nombre de usuario: ".encode())
        username = self.client_socket.recv(1024).decode()
        self.verify_back(username) #
        self.client_socket.send("Ingrese su contraseña: ".encode())
        password = self.client_socket.recv(1024).decode()
        self.verify_back(password) #

        self.client_socket.send("Ingrese su correo electrónico: ".encode())
        email = self.client_socket.recv(1024).decode()
        self.verify_back(email) #
        
        # Crear un nuevo usuario con los datos ingresados
        data = {
            "username": username,
            "password": password,
            "email": email
        }
        self.local_node.store_data(self.user.username, data)
        # Asignar el usuario a la variable user y cambiar logged_in a True
        self.logged_in = True
        #user = User(username, password, email)

    def profile(self):
        user_tweets = self.local_node.retrieve_data(self.user.username, "tweets") ########################################
        user_retweets = self.local_node.retrieve_data(self.user.username, "retweets")
        posts = []
        posts.extend(user_tweets)
        posts.extend(user_retweets)
        
        # Sorted by date created (recents first)
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return posts

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

    def logout(self):
        self.logged_in = False
        self.user = None

    def verify_back( self, option ):
        if option == "b":
            self.home()
        else:
            return