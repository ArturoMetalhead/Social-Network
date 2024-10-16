import json
import string
import secrets
import time
import heapq
import random
import os

alphabet = string.ascii_letters + string.digits

# Tipos de Nodos
CLIENT = 0
ENTRY_POINT = 1
LOGGER = 2
CHORD = 3
CHORD_INTERNAL = 4
TWEET = 5

# Protocolos de pedidos
LOGIN_REQUEST = 0
LOGIN_RESPONSE = 1
CHORD_REQUEST = 2
CHORD_RESPONSE = 3
NEW_LOGGER_REQUEST = 4
NEW_LOGGER_RESPONSE = 5
ALIVE_REQUEST = 6
ALIVE_RESPONSE = 7
REGISTER_REQUEST = 8 
REGISTER_RESPONSE = 9
TRANSFERENCE_REQUEST = 10
TRANSFERENCE_RESPONSE = 11
TRANSFERENCE_OVER = 12
CREATE_TWEET_REQUEST = 13
CREATE_TWEET_RESPONSE = 14
RETWEET_REQUEST=15
RETWEET_RESPONSE =16
FOLLOW_REQUEST = 17
FOLLOW_RESPONSE = 18
FEED_REQUEST = 19
FEED_RESPONSE = 20
PROFILE_REQUEST =21
PROFILE_RESPONSE = 22
NEW_ENTRYPOINT_REQUEST = 23
NEW_ENTRYPOINT_RESPONSE = 24
LOGOUT_REQUEST = 25
LOGOUT_RESPONSE = 26
GET_TOKEN = 27
RECENT_PUBLISHED_REQUEST = 28
RECENT_PUBLISHED_RESPONSE = 29
CHECK_TWEET_REQUEST = 30
CHECK_TWEET_RESPONSE = 31
ADD_LOGGER = 32
REMOVE_LOGGER = 33
ADD_ENTRY = 34
REMOVE_ENTRY = 35
INSERTED_LOGGER_REQUEST = 36
INSERTED_LOGGER_RESPONSE = 37
CHECK_USER_REQUEST = 38
CHECK_USER_RESPONSE = 39
GET_TWEET = 40
PROFILE_GET = 41
HELLO = 42
WELLCOME = 43
HARD_WRITE = 44
PROFILE_DATA_REQUEST = 45
ADD_TWEET = 46
ADD_RETWEET = 47
ADD_PROFILE = 48
ADD_FOLLOW = 49
ADD_TOKEN = 50
REMOVE_TOKEN = 51

# Puertos de escucha
PORT_GENERAL_ENTRY = 15069
CHORD_PORT = 15042
PORT_GENERAL_LOGGER = 15071

def encode(data_dict):
    '''
    Codifica un diccionario de Python a bytes
    '''
    return json.dumps(data_dict).encode()

def decode(data_bytes):
    '''
    Decodifica bytes para interpretarlo como diccionario de Python
    '''
    return json.loads(data_bytes)

def gen_token(n_bytes):
    return ''.join(secrets.choice(alphabet) for i in range(n_bytes))


class Dispatcher:

    def __init__(self):
        self.__next_petition_id = 0
        self.petitions = {}
        self.slaves = None

    def insert_petition(self, petition):
        ret = self.__next_petition_id
        self.petitions[ret] = petition
        self.__next_petition_id += 1
        return ret

    def extract_petition(self, id):
        return self.petitions.get(id, None)


class Stalker:
    '''
    Estructura que guarda una lista de IP:Puertos (o Puertos),
    con la ultima hora de actividad. Recomienda de forma aleatoria un IP
    para verificar si est'a vivo a'un, pero dando mas probabilidad a los
    IP menos actualizados.
    '''
    def __init__(self, type, umbral_alive = 90, umbral_deads=30):
        '''
        Inicializa la estructura Stalker con el tipo de Server que la aloje.
        Internamente utiliza una lista con tuplas de la forma (tiempo, IP:Port)
        '''
        self.list = []
        self.type = type
        self.umbral_alive = umbral_alive
        self.umbral_deads = umbral_deads
        self.alive_dirs = []
        self.deads_dirs = []

    def insert_IP(self, dir):
        '''
        Agrega una nueva direcci'on IP a la lista. La presupone nueva.
        Utilizar mejor update cuando no se tiene la certeza de su existencia.        
        '''
        self.list.append((time.time(), dir))

    def update_IP(self, dir):
        '''
        Actualiza el tiempo de un IP. Si este est'a solamente se actualiza el tiempo
        con el tiempo actual. Si no est'a, se a~nade nuevo.
        '''
        for i, item in enumerate(self.list):
            if item[1] == dir:
                self.list[i] = (time.time(), dir)
                self.list.sort()
                return True
        self.list.append((time.time(), dir))
        return False

    def extract_IP(self, dir):
        '''
        Se elimina el IP de la lista y se retorna su valor. Si este no existe
        se retorna None
        '''
        for i, item in enumerate(self.list):
            if item[1] == dir:
                return self.list.pop(i)
        return None
    
    def recommended_dir(self):
        '''
        Se recomienda alg'un IP de la lista. Mientras m'as viejo, m'as probable
        eres de ser recomendado.
        '''
        _, dir = random.choices(self.list,weights=range(len(self.list), 0, -1),k=1)[0]
        return dir
    
    def refresh_dirs(self):

        self.alive_dirs = []
        real_time = time.time()
        self.deads_dirs = []
        for i in range(len(self.list)):
            t, dir = self.list[i]
            if real_time - t >= self.umbral_deads:
                self.deads_dirs.append(dir)
            if real_time - t <= self.umbral_alive:
                self.alive_dirs.append(dir)
        return self.deads_dirs.copy()

    def msg_stalk(self):
        '''
        Genera el mensaje de ALIVE_REQUEST
        '''
        msg = {
            'type': self.type,
            'proto': ALIVE_REQUEST, # Definir el protocolo de estar vivo.
        }
        return msg


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

class Cache:

    def __init__(self) -> None:
        self.profiles = {}

    def add_something(self, date, text, nick, nick_original, date_original):
        profile = self.profiles.get(nick, None)
        if profile is None:
            self.profiles[nick] = {}
        self.profiles[nick][date] = (text, nick_original, date_original)

    def add_many_something(self, list):
        for date, text, nick, nick_original, date_original in list:
            self.add_many_something(date, text, nick, nick_original, date_original)
        
