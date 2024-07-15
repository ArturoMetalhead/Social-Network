from server import *
import threading

operators = [('localhost', 8080)]
twitter_servers = [('localhost', 8083), ('localhost', 8084), ('localhost', 8085)]

operators2 = [('localhost', 8081), ('localhost', 8080)]


def main():

    # servers=['127.0.0.1:4041','127.0.0.2:4042']
    server_manager = Server_Manager(operators,twitter_servers,'localhost',8080)
    server_manager2 = Server_Manager(operators2,twitter_servers,'localhost',8081)

    T1=threading.Thread(target=server_manager.start_operator)
    T2=threading.Thread(target=server_manager2.start_operator)

    T1.start()
    T2.start()




if __name__ == "__main__":
    main()