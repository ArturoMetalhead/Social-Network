from thread_holder import Thread_Holder
from chord.chord_utils import Number_Assigment, TwoBase
from threading import Lock
import json
from math import floor , log2

class State_Storage():
    def __init__(self):
        self.storage: dict[int, Thread_Holder] = {}
        self.lock = Lock()
        self.id_gen = Number_Assigment()

    def insert_state(self):
        """
        Insert a new state.
        """
        id = self.id_gen.get_id()
        state = Thread_Holder(id)
        with self.lock:
            self.storage[state.id] = state
        return state
    
    def delete_state(self, id):
        """
        Delete a state.
        """
        with self.lock:
            item = self.storage.pop(id, None)
            if item:
                self.id_gen.free_id(id)

    def get_state(self, id) -> Thread_Holder:
        """
        Get a state.
        """
        with self.lock:
            value = self.storage.get(id, None)
        return value

class ChordNode():
    def __init__(self, id, id_hex, ip_list, as_max):
        self.id = TwoBase(id, id_hex)
        self.ip_list = ip_list
        self.as_max = as_max

    def __str__(self):
        d = {
            'id_hex': self.id.hex,
            'ip_list': self.ip_list,
            'as_max': self.as_max
        }
        return json.dumps(d)
    
    def build_from_message(s):
        if s == 'none':
            return None
        d = json.loads(s)
        return ChordNode(int(d['id_hex'],16),d['id_hex'],d['ip_list'],d['as_max'])
    
class Chord_Server():
    def __init__(self, DHT_name, port, disable_log, id_hex=None, print_table = False):
        self.DHT_name = DHT_name
        self.port = port
        self.print_table - print_table
        self.Ft_lock = Lock()
        self.Ft: list[tuple[ChordNode,bool]] = [None]*floor(log2(self.max_id + 1))

    def insert_as_first(self):
        '''
        Insert a new node into the DHT as the first node.
        '''
        num = self.id + self.max_id # calculate a new number bigger than any node in the chord network
        num_hex = hex(num)[2:] # getting hexadecimal representation (excludes initial 0x)

        # creating new instances ###########################################
        self.Ft[0] = (ChordNode(num ,num_hex ,self.reps ,as_max=True),True)
        self.Ft[1] = (ChordNode(num ,num_hex ,self.reps ,as_max=True),True)

        # Fill the finger table 
        for i in range(2 ,len(self.Ft)):
            self.Ft[i] = self.Ft[1]
