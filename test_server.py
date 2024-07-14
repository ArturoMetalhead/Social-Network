
from server import *


def main():

    servers=['127.0.0.1:4041','127.0.0.2:4042']
    server_manager = Server_Manager()
    server_manager.start_server()


if __name__ == "__main__":
    main()

