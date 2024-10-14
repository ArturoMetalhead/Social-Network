import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event, Lock
import hashlib
import random
import datetime


try:
    from messages import *
    import util
    from server import Server
    from util import *
    from threaded_server import MultiThreadedServer
except:
    from API.messages import *
    import API.util as util
    from API.server import Server
    from API.util import *
    from API.threaded_server import MultiThreadedServer

NEW_NODE = 0
REPLIC_NODE = 1

USER_TABLE = 1
TOKEN_TABLE = 2
TWEET_TABLE = 3
RETWEET_TABLE = 4
FOLLOW_TABLE = 5
class TweeterServer(MultiThreadedServer):
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int):

        MultiThreadedServer.__init__(self,port, task_max, thread_count, timout, self.switch)
        
        self.entry_point_ips = []
        self.node_sibiling = []
        self.primary = []
        self.siblings = []
        self.is_primary = False
        self.my_ip = socket.gethostbyname(socket.gethostname())

        self.pending_tasks = {}
        self.execute_pending_tasks = False
        self.lock_tasks = Lock()
        
        with open('entrys.txt', 'r') as ft:
            for ip in ft.read().split(sep='\n'):
                self.entry_point_ips.append(str(ip))                
        self.current_index_entry_point_ip = random.randint(0, len(self.entry_point_ips))
        self.chord_id = None

    def switch(self, id:int, task: tuple[socket.socket,object], event:Event, storage):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        ---------------------------------------
        `data_dict['type']`: Tipo de peticion
        '''
        print("\n ME ESCRIBIERON UwU \n")
        (socket_client, addr_client) = task
        data_byte = socket_client.recv(15000)
        
        try:
            data_dict = util.decode(data_byte)
            type_rqst = data_dict["type"]       
            proto_rqst = data_dict["proto"]
        
        except Exception as e:
            print(e)
            return
        
        print('Switch del Logger')
        print(type_rqst, proto_rqst)
        print(data_dict)
        if type_rqst == CHORD:
            
            if proto_rqst == NEW_LOGGER_REQUEST:
                self.new_logger_response(socket_client, addr_client, data_dict,storage)
            
        if type_rqst == ENTRY_POINT:
            
            if proto_rqst == LOGIN_REQUEST:
                self.login_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                self.logout_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == REGISTER_REQUEST:
                self.register_request(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst in  (CREATE_TWEET_REQUEST, FOLLOW_REQUEST, RETWEET_REQUEST, FEED_REQUEST, PROFILE_REQUEST):
                self.tweet_request(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst == ALIVE_REQUEST:
                self.alive_request(socket_client, addr_client, data_dict, storage)
                      
        elif type_rqst == LOGGER:
            
            if proto_rqst == LOGIN_REQUEST:
                self.get_token(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                self.get_logout(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == REGISTER_REQUEST:
                self.get_register(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst in  (LOGIN_RESPONSE, REGISTER_RESPONSE, CHORD_RESPONSE, LOGOUT_RESPONSE): 
                self.set_data(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == HELLO:
                self.say_welcome(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == TRANSFERENCE_REQUEST:
                self.data_transfer(socket_client, addr_client, data_dict, storage)

            
        elif type_rqst == TWEET:
            
            if proto_rqst == CREATE_TWEET_REQUEST:
                self.create_tweet(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == FOLLOW_REQUEST:
                self.create_follow(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == RETWEET_REQUEST: 
                self.create_retweet(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == GET_TWEET:
                self.tweet_check(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == FEED_REQUEST:
                self.feed_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == PROFILE_DATA_REQUEST:
                self.profile_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == PROFILE_REQUEST:
                self.profile_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == RECENT_PUBLISHED_REQUEST:
                self.recent_publish(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == CHECK_TWEET_REQUEST:
                self.tweet_check(socket_client, addr_client, data_dict, storage)
            elif proto_rqst in (CREATE_TWEET_RESPONSE, FOLLOW_RESPONSE, RETWEET_RESPONSE, FEED_RESPONSE, PROFILE_RESPONSE, RECENT_PUBLISHED_RESPONSE, CHECK_TWEET_RESPONSE, CHECK_USER_RESPONSE):
                self.set_data(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == CHECK_USER_REQUEST:
                self.nick_check(socket_client, addr_client, data_dict,storage)
            
            elif proto_rqst == ADD_TWEET:
                socket_client.close()
                self.add_tweet_from_logger(data_dict)
            elif proto_rqst == ADD_RETWEET:
                socket_client.close()
                self.add_retweet_from_logger(data_dict)
            elif proto_rqst == ADD_PROFILE:
                socket_client.close()
                self.add_profile_from_logger(data_dict)
            elif proto_rqst == ADD_FOLLOW:
                socket_client.close()
                self.add_follow_from_logger(data_dict)
            elif proto_rqst == ADD_TOKEN:
                socket_client.close()
                self.add_token_from_logger(data_dict)
            elif proto_rqst == REMOVE_TOKEN:
                socket_client.close()
                self.remove_follow_from_logger(data_dict)
        
        else: 
            pass
        #TODO error de tipo
        
    def register_request(self, socket_client, addr_client, data_dict, storage):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `data_dict['name']`: Nombre de usuario
        `data_dict['nick']`: Alias de usuario
        `data_dict['password']`: Contrasenna
        '''
        socket_client.close()
        #pedir un evento para m\'aquina de estado 
        nick = data_dict['nick']
        state = do_chord_sequence(storage, nick)

        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            data = register_request_msg(data_dict['name'],nick, data_dict["password"], state2.id)
            send_and_close(random.choice(state.desired_data['IP']), PORT_GENERAL_LOGGER, data)
            state = wait_get_delete(storage, state2)
            
            if state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']
                    print("PSSSSS")
                    print("PSSSSS")
                    print("PSSSSS")
                    send_and_close(addr_client[0], PORT_GENERAL_ENTRY, state.desired_data)
                    return
                except:


                    pass
        data = register_response_msg(False, 'Something went wrong in the network connection', data_dict['id_request'])
        send_and_close(addr_client[0],PORT_GENERAL_ENTRY, data)
  
    def login_request(self, socket_client, addr_client, data_dict, storage):
        '''
        Solicitud de inicio de sesion de usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['password']`: Contrasenna
        '''

        socket_client.close()
        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        state = do_chord_sequence(storage,nick)
        print('Llego el CHORD')
        print(state.desired_data)        
        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            data = login_request_msg(nick, data_dict["password"], state2.id)
            send_and_close(state.desired_data['IP'][0],PORT_GENERAL_LOGGER, data)
            print('Send an Close')
            state = wait_get_delete(storage, state2)
            print('Wait', state.desired_data)
            if state and state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']
                    send_and_close(addr_client[0], PORT_GENERAL_ENTRY, state.desired_data)
                    return

                except:
                    pass
        print('Hubo error')
        data = login_response_msg(False, None, 'Something went wrong in the network connection', data_dict['id_request'])
        send_and_close(addr_client[0], PORT_GENERAL_ENTRY, data)

    def logout_request(self, socket_client, addr_client, data_dict, storage):
        

        socket_client.close()
        nick = data_dict['nick']
        state = do_chord_sequence(storage, nick)
        print('Logout', state.desired_data)
        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            data = logout_request_msg(nick, data_dict["token"], state2.id)
            print('Data', data)
            send_and_close(state.desired_data['IP'][0],PORT_GENERAL_LOGGER, data)
            state = wait_get_delete(storage, state2)
            print('luego del WWWWWAAAAAIIIITTTT')
            if state and state.desired_data:
                #reenviar mensaje de autenticacion
                print('State BIEEEEEEEEEN')
                print(state.desired_data)
                try:
                    state.desired_data['id_request'] = data_dict['id_request']
                    send_and_close(addr_client[0], PORT_GENERAL_ENTRY, state.desired_data)
                    return
                except:
                    pass
        data = logout_response_msg(False, 'Something went wrong in the network connection', data_dict['id_request'])
        send_and_close(addr_client[0], PORT_GENERAL_ENTRY, data)
       
    
    def alive_request(self, socket_client, addr_client, data_dict, storage):
        data = {
            'type': LOGGER,
            'proto': ALIVE_RESPONSE,
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    def tweet_request(self, socket_client, addr_client, data_dict, storage): 

        print('Tweet Request')
        print(data_dict)
        socket_client.close()    
        #pedir un evento para m\'aquina de estado 
        nick = data_dict['nick']
        id_request = data_dict['id_request']
        state = do_chord_sequence(storage, nick)
        print('Tweet Request CHORD', state)
        print('Desired', state.desired_data)
        print('IPs', state.desired_data['IP'])
        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            print('State2')
            data_dict['type'] = TWEET
            data_dict['id_request'] = state2.id
            print(data_dict['type'])
            send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data_dict)
            state = wait_get_delete(storage, state2)
            
            if state and state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['type'] = LOGGER
                    state.desired_data['id_request'] = id_request
                    print("DATA ENVIADA AL ENTRY:", state.desired_data)
                    send_and_close(addr_client[0],PORT_GENERAL_ENTRY, state.desired_data)
                    return
                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': data_dict['proto'] +1,
                'succesed': False,
                'error': 'Something went wrong in the network connection',
                'id_request':  id_request
        }
        send_and_close(addr_client[0], PORT_GENERAL_ENTRY, data)

    
    def update_info(self, info, table):
        data_dict = {
            'type': TWEET,
            'proto': HARD_WRITE,
            'data': info,
            'table': table
        }
        
        for ip in self.primary:
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((ip, PORT_GENERAL_LOGGER))
            skt.send(util.encode(data_dict))
            skt.close() 



    def say_hello(self):        
        print('dentro del SAY HELLO')
        data = {
            'type': LOGGER,
            'proto': HELLO
        }
        sibs = self.siblings.copy()

        while len(sibs) > 0:
            i = 0
            while i < len(sibs):
                try:
                    skt = socket.socket(AF_INET, SOCK_STREAM)
                    skt.connect((sibs[i], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data))
                    data_x = skt.recv(1024)
                    data_x = util.decode(data_x)
                    skt.close()
                    with self.lock_tasks:
                        if self.pending_tasks.get(sibs[i], None) is None:
                            self.pending_tasks[sibs[i]] = []
                    sibs.pop(i)
                    i -= 1
                except:
                    pass
                i+=1
            time.sleep(random.randint(1,6))
        


    def say_welcome(self, socket_client, addr_client, data_dict, storage):
        
        data = {
            'type': LOGGER,
            'proto': WELLCOME,            
        }
        try:
            socket_client.send(util.encode(data))
            socket_client.close()            
        except:
            print('NO wellcome')
            return

        with self.lock_tasks:
            if self.pending_tasks.get(addr_client[0], None) is None:
                self.pending_tasks[addr_client[0]] = []

    #--------------------------

    def add_task(self, proto, data):
        for ip, tasks in self.pending_tasks.items():
            tasks.append((proto, data))

    def send_pending_tasks(self, event: Event):
        self.execute_pending_tasks = True        
        while not event.is_set():
            print('Tareas Pendientes:')
            print(self.pending_tasks)
            for ip, tasks in self.pending_tasks.items():
                print('IMPRIMIENDO TAREAS')                
                print(tasks)
                i = 0
                while i < len(tasks):                    
                    try:
                        msg = {
                            'type':  TWEET,
                            'proto': tasks[i][0],
                            'data':  tasks[i][1]
                        }
                        s = socket.socket(AF_INET, SOCK_STREAM)
                        s.connect((ip, PORT_GENERAL_LOGGER))
                        s.send(util.encode(msg))
                        s.close()
                        print(f'TAREA PENDIENTE "{tasks[i][0]}:{tasks[i][1]}" ENVIADA a {ip}:{PORT_GENERAL_ENTRY}')
                        tasks.pop(i)
                        i -= 1
                    except:
                        print(f'TAREA PENDIENTE "{tasks[i][0]}:{tasks[i][1]}" NO enviada a {ip}:{PORT_GENERAL_ENTRY}')
                        break
                    i += 1
                    event.wait(random.randint(1,5))
            event.wait(random.randint(4,10))
        self.execute_pending_tasks = False
        print('END Pending Tasks')