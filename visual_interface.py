
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

import os
from colorama import init, Fore, Back, Style

init(autoreset=True)

logged_in = False
user = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(Fore.CYAN + "=" * 50)
    print(Fore.YELLOW + "        BIENVENIDO A NUESTRA RED SOCIAL        ")
    print(Fore.CYAN + "=" * 50)

def print_footer():
    print(Fore.CYAN + "=" * 50)
    print(Fore.YELLOW + "          GRACIAS POR USAR NUESTRA APP    ")
    print(Fore.CYAN + "=" * 50)

def print_menu(options):
    for i, option in enumerate(options, 1):
        print(f"{Fore.GREEN}{i}. {Fore.WHITE}{option}")

def get_user_choice(options):
    while True:
        try:
            choice = int(input(Fore.YELLOW + "\nIngrese una opción: "))
            if 1 <= choice <= len(options):
                return choice
            else:
                print(Fore.RED + "Opción inválida. Intente de nuevo.")
        except ValueError:
            print(Fore.RED + "Por favor, ingrese un número válido.")

def home():
    clear_screen()
    print_header()
    
    if logged_in:
        print(Fore.CYAN + f"\nBienvenido, {user.username}!")
        options = ["Ver perfil", "Ver seguidores", "Ver seguidos", "Publicar", "Cerrar sesión"]
        print_menu(options)
        choice = get_user_choice(options)
        
        actions = [profile, followers, followings, post, logout]
        actions[choice - 1]()
    else:
        options = ["Iniciar sesión", "Registrarse"]
        print_menu(options)
        choice = get_user_choice(options)
        
        actions = [login, register]
        actions[choice - 1]()
    
    print_footer()


def login():
    global logged_in
    global user
    username = input(Fore.YELLOW + "Ingrese su nombre de usuario: ")
    verify_back(username) #
    password = input("Ingrese su contraseña: ")
    verify_back(password) #
    
    # Verificar si el usuario y contraseña son correctos
    # Si son correctos, asignar el usuario a la variable user y cambiar logged_in a True
    # Si no son correctos, imprimir un mensaje de error

    if verify_user(username, password):
        logged_in = True

    #user = User(username, password, " ")

def register():
    global logged_in
    global user
    username = input(Fore.YELLOW + "Ingrese su nombre de usuario: ")
    verify_back(username) #
    password = input("Ingrese su contraseña: ")
    verify_back(password) #
    email = input("Ingrese su correo electrónico: ")
    verify_back(email) #
    
    # Crear un nuevo usuario con los datos ingresados
    # Asignar el usuario a la variable user y cambiar logged_in a True
    logged_in = True
    #user = User(username, password, email)

def profile():
    # Extraer publicaciones hechas por el usuario
    pass

def followings():
    # Extraer usuarios seguidos por el usuario
    pass

def followers():
    # Extraer seguidores del usuario
    pass

def post():
    # Crear una nueva publicación
    pass

def logout():
    global logged_in
    global user
    logged_in = False
    user = None

def verify_back( option ):
    if option == "b":
        home()
    else:
        return



if __name__ == "__main__":
    while True:
        home()

