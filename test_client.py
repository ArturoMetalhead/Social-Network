from client import *


operators = [('127.0.0.1', 8080), ('127.0.0.2', 8081)]


def main():
    client_manager = Client_Manager(operators)
    client_manager.start_client()


if __name__ == "__main__":
    main()