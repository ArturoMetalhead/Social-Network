from socket import socket
from thread_holder import Thread_Holder
from chord.chord_utils import Number_Assigment, TwoBase, get_my_ip
from threading import Lock
import json
from math import floor , log2
from time import sleep
from datetime import datetime
from random import randint, shuffle
from socket import socket , AF_INET , SOCK_STREAM ,gethostbyname ,gethostname
from hashlib import shake_256
from math import floor , log2
import hashlib

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

class Chord_Node():
    def __init__(self, id, id_hex, ip_list, as_max):
        self.id = TwoBase(id, id_hex)
        self.ip_list = ip_list
        self.as_max = as_max

    def __str__(self):
        '''
        Return a string representation of the ChordNode.
        '''
        d = {
            'id_hex': self.id.hex,
            'ip_list': self.ip_list,
            'as_max': self.as_max
        }
        return json.dumps(d)
    
    def build_from_message(s):
        '''
        Build a ChordNode from a message.
        '''
        if s == 'none':
            return None
        d = json.loads(s)
        return Chord_Node(int(d['id_hex'],16),d['id_hex'],d['ip_list'],d['as_max'])
    
class Chord_Server():
    def __init__(self, DHT_name, port, disable_log, id_hex=None, print_table = False):
        self.DHT_name = DHT_name
        self.port = port
        self.ip = get_my_ip()
        self.id_hex = None
        self.print_table - print_table
        self.Ft_lock = Lock()
        self.Ft: list[tuple[Chord_Node,bool]] = [None]*floor(log2(self.max_id + 1))
        self.log = []
        self.log_lock = Lock()
        self.request_count = {}
        self.reps = [self.ip]

        self.state_storage = State_Storage()

        # Comunication commands
        self.get_succ_req = 'get_succ_req'
        self.ImYSucc_cmd = 'ImYSucc'
        self.ImYPrev_cmd = 'ImYPrev'
        self.ImYRep_cmd = 'ImYRep'
        self.outside_cmd = 'outside'
        self.confirm_cmd = 'confirm_new_succ'
        self.new_rep_cmd = 'new_rep'
        self.new_succ_cmd = 'new_succ'
        self.new_prev_cmd = 'new_prev'
        self.get_reps_cmd = 'get_reps'

        # Hex ID assigment
        if id_hex == None: 
            self.id_hex = hashlib.sha256(self.ip.encode()).hexdigest()
            self.id = int(self.id_hex ,16)
        else:
            self.id_hex = id_hex
            self.id = int(id_hex,16)

    # region Insertions

    def insert_as_first(self):
        '''
        Insert a new node into the DHT as the first node.
        '''
        num = self.id + self.max_id # calculate a new number bigger than any node in the chord network
        num_hex = hex(num)[2:] # getting hexadecimal representation (excludes initial 0x)

        # creating new instances ###########################################
        self.Ft[0] = (Chord_Node(num ,num_hex ,self.reps ,as_max=True),True)
        self.Ft[1] = (Chord_Node(num ,num_hex ,self.reps ,as_max=True),True)

        # Fill the finger table 
        for i in range(2 ,len(self.Ft)):
            self.Ft[i] = self.Ft[1]

    def insert(self, ips):
        node = self.ask_succ(ips, self.id_hex, False)
        prev = None
        succ = None

        if node.id.hex == self.id_hex:
            prev, succ = self.insert_rep(node)
        else:
            prev, succ = self.insert_new_node(ips, node)
        
        self.Ft[0] = (prev, self.ip in prev.ip_list)
        me_as_succ = self.ip in succ.ip_list

        for i in range(1 ,len(self.Ft)):
            self.Ft[i] = (succ,me_as_succ)

    def insert_new_node(self, ips, succ_node):
        response = 'Busy'
        while response == 'Busy':
            response, prev_node = self.ImYPrev(succ_node)
            
            if response != 'Busy':
                break
            self.update_log(f'{succ_node.ip} is busy')
            sleep(randint(1,5))
            succ_node = self.ask_succ(ips, self.id_hex, False)
        
        self.ImYSucc(prev_node)
        self.confirm_new_prev(succ_node)
        return prev_node, succ_node
    
    def insert_rep(self, rep_node):
        '''
        Inserts a node that already exists in the Chord network and needs to be reinserted or upgraded.

        Params:
            rep_node: A ChordNode object that represents the node being inserted or updated.
        '''
        response = 'Busy'
        
        while response == 'Busy':
            response, prev_node, succ_node, reps = self.ImYRep(rep_node)

            if response != 'Busy':
                break
            self.update_log(f'{succ_node.ip_list} is busy')
            sleep(randint(1,5))
        
        for rep in reps:
            if rep != self.ip:
                self.reps.append(rep)
        self.new_rep(rep_node)
        return prev_node, succ_node

    # endregion

    # region Prev and Succesor 

    def ask_succ(self, ips, id_hex, as_max) -> Chord_Node:
        '''
        Get the successor of the current node.
        Params:
            ips: str -> ips to send the request to
            id_hex: int -> hexadecimal representation of the id
            as_max: bool -> if the node is the maximum node
        '''
        holder = self.state_storage.insert_state()

        while(True):
            for _ in range(10):
                msg = Chord_Server.create_msg(cmd = self.get_succ_req ,id_hex = id_hex ,owner_ip = self.ip ,as_max = as_max ,req_id = holder.id)
                self.update_log(f'starting to send (ask_succ to {ips} for {id_hex} as_max:{str(as_max)})')                
                self.send_til_success(ips ,msg ,'ask_succ',self.port)
                self.update_log(f'waiting for response in ask_succ')                

                holder.hold_event.wait(5)
                if holder.desired_data:
                    self.state_storage.delete_state(holder.id)
                    break
            if holder.desired_data:
                break
            self.update_log('timout waiting 10 times')
            sleep(2)
        return holder.desired_data
    
    def ImYPrev(self, succ: Chord_Node):
        msg = Chord_Server.create_msg(cmd = self.ImYPrev_cmd, id_hex = self.id_hex, owner_ip = self.reps)

        self.update_log('starting to send (ImTPrev)')

        response = self.send_til_success(succ.ip_list, msg, 'ImYPrev', self.port)

        arr = json.loads(response)
        return arr[0], Chord_Node.build_from_message(arr[1])
    
    def ImYSucc(self, prev: Chord_Node):
        msg = Chord_Server.create_msg(cmd = self.ImYSucc_cmd, id_hex = self.id_hex, owner_ip = self.ip)
        self.update_log('starting to send (ImYSucc)')
        self.send_til_success(prev.ip_list, msg, 'ImYSucc', self.port)

    def confirm_new_prev(self, succ:Chord_Node):
        msg = Chord_Server.create_msg(cmd = self.confirm_cmd, id_hex = self.id_hex, owner_ip = self.ip)
        self.update_log('starting to send (confirm)')
        self.send_til_success(succ.ip_list ,msg ,'confirm',self.port)
    
    def ImYRep(self, rep_node: Chord_Node):
        msg = Chord_Server.create_msg(cmd = self.ImYRep_cmd, owner_ip = self.ip)

        self.update_log('starting to send (ImYRep)')
        response = self.send_til_success(rep_node.ip_list, msg, 'ImYRep', self.port)
        arr = json.loads(response)

        return arr[0], Chord_Node.build_from_message(arr[1]), Chord_Node.build_from_message(arr[2]), arr[3]
    
    # endregion

    def create_msg(**kwargs):
        '''
        Create a message.
        '''
       # kwargs['type'] = #############################################################################
        return json.dumps(kwargs)
    
    def update_log(self, entry):
        '''
        Update the log with an entry.
        '''
        with self.log_lock:
            if entry:
                self.log.append((entry ,str(datetime.datetime.now().time())))
        return

    # region Conections and communication
    def send_til_success(self, ips, msg, req, port):
        '''
        Send a message until a response is received.
        '''
        response = None
        while not response:
            response = self.send_and_close(ips ,msg ,port)
            if not response:
                self.update_log(f'failed to send {req} to {ips}:{port}')
                sleep(2)
        return response
    
    def send_and_close(self, ips, msg, port, have_recv = True):
        response = None
        if ips:
            shuffle(ips)
        for ip in ips:
            for _ in range(10):    
                try:
                    s = socket(AF_INET ,SOCK_STREAM)
                    self.update_log(f'connecting to {ip}:{port}')
                    s.connect((ip ,port))   
                    s.send(msg.encode())
                    if have_recv:          
                        response = s.recv(15000)
                    else:
                        response = 'Ok'
                    s.close()
                    if not (response == None):
                        if ip in self.request_count.keys():
                            self.request_count[ip] += 1
                        else:
                            self.request_count[ip] = 1
                        break
                except Exception as e:
                    print(e)
                    self.update_log(str(e)) 
            if not (response == None):
                break
        self.update_log('send ended')
        return response
    
    # endregion