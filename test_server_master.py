
from server_master import *

def main():
    servermaster_operators=Server_Master(ip='localhost',port=8088,id_type_server=1)
    servermaster_twitter=Server_Master(ip='localhost',port=8089,id_type_server=2)

    T1=threading.Thread(target=servermaster_operators.start_server)
    T2=threading.Thread(target=servermaster_twitter.start_server)

    T1.start()
    T2.start()


if __name__ == "__main__":
    main()