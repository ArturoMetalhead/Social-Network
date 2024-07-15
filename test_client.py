from client import *


operators = [('localhost', 8080), ('localhost', 8081), ('localhost', 8082)]


def main():
    client_manager = Client_Manager(operators)
    client_manager.start_client()


if __name__ == "__main__":
    main()