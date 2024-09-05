from operator_server import *
import threading

#operators = []
#operators=[]
twitter_servers = [('localhost', 8083), ('localhost', 8084), ('localhost', 8085)]

#operators2 = [('localhost', 8080)]
#operators2=[('localhost', 5000)]
#operators2=[]


def main():

    # servers=['127.0.0.1:4041','127.0.0.2:4042']
    server_manager = Operator_Server([],'127.0.0.1',8080) ####el agrega el ip como localhost de otra manera y lo guardara 2 veces como 127.0.0.1 y como localhost
    server_manager2 = Operator_Server([],'127.0.0.2',8081)

    T1=threading.Thread(target=server_manager.start_operator_server)
    T2=threading.Thread(target=server_manager2.start_operator_server)

    T1.start()
    T2.start()

    # #dormir por 30 segundos
    # time.sleep(30)
    # server_manager.stop_server()
    # time.sleep(30)
    # server_manager2.stop_server()




if __name__ == "__main__":
    main()