from twitter_server import *
from chord.chord import *
import threading

twitter_servers = [('localhost', 8083), ('localhost', 8084), ('localhost', 8085)]
twitter_servers2 = [('localhost', 8084), ('localhost', 8085), ('localhost', 8083)]
twitter_servers3 = [('localhost', 8085), ('localhost', 8083), ('localhost', 8084)]

#chord_node = ChordNode(1, 'localhost', 8089, 3)
chord_node = None


def main():

    # servers=['127.0.0.1:4041','127.0.0.2:4042']


    server_manager = Twitter_Server(chord_node)
    server_manager2 = Twitter_Server(chord_node)
    server_manager3 = Twitter_Server(chord_node)

    T1=threading.Thread(target=server_manager.start_server)
    T2=threading.Thread(target=server_manager2.start_server)
    T3=threading.Thread(target=server_manager3.start_server)

    T1.start()
    T2.start()
    T3.start()
    


if __name__ == "__main__":
    main()