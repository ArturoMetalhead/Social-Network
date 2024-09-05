from socket import socket
from thread_holder import Thread_Holder
import sys
sys.path.append('../Social-Network')
from chord_utils import Number_Assigment, TwoBase, get_my_ip
from threading import Lock, Thread, Event
import json
from math import floor , log2
from time import sleep
from datetime import datetime
from random import randint, shuffle
from socket import socket , AF_INET , SOCK_STREAM ,gethostbyname ,gethostname
from hashlib import shake_256
from math import floor , log2
import hashlib
import protocols

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
        self.print_table = print_table
        self.Ft_lock = Lock()
        self.max_id = int(''.join(['f' for _ in range(64)]) ,16)
        self.Ft: list[tuple[Chord_Node,bool]] = [None]*floor(log2(self.max_id + 1))
        self.log = []
        self.log_lock = Lock()
        self.busy_lock = Lock()
        self.request_count = {}
        self.reps = [self.ip]
        self.state_storage = State_Storage()
        self.server = socket(AF_INET, SOCK_STREAM)

        # Comunication commands
        self.get_succ_req = 'get_succ_req'
        self.get_succ_resp_cmd = 'get_succ_resp'
        self.ImYSucc_cmd = 'ImYSucc'
        self.ImYPrev_cmd = 'ImYPrev'
        self.ImYRep_cmd = 'ImYRep'
        self.outside_cmd = 'outside'
        self.confirm_cmd = 'confirm_new_succ'
        self.new_rep_cmd = 'new_rep'
        self.new_succ_cmd = 'new_succ'
        self.new_prev_cmd = 'new_prev'
        self.get_reps_cmd = 'get_reps'

        self.request_handler = {
            self.get_succ_req: self.get_succ_req_handler, # implemented
            self.get_succ_resp_cmd:self.get_succ_resp_handler, #implemented
            self.ImYSucc_cmd: self.ImYSucc_handler, # implemented
            self.ImYPrev_cmd: self.ImYPrev_handler, # implemented
            self.ImYRep_cmd: self.ImYRep_handler, #implemented
            self.outside_cmd: self.outside_handler, # implemented
            self.confirm_cmd: self.confirm_new_prev_handler, # implemented
            self.new_rep_cmd: self.new_rep_handler, # implemented
            self.new_succ_cmd: self.new_succ_handler, # implemented
            self.new_prev_cmd: self.new_prev_handler, # implemented
            self.get_reps_cmd: self.get_reps_handler #implemented
        }

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
        '''
        Insert a new node into the DHT.

        Params:
            ips: str -> ips to send the request to
            succ_node: ChordNode -> the successor node
        '''
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
    
    def succ_who(self, k, as_max):
        res_id = self.id
        res_hex = self.id_hex

        if as_max:
            k = k - self.max_id
            res_id += self.max_id
            res_hex = hex(res_id)[2:]

        # if is this
        if(self.Ft[0][0].id.dec < k or as_max or self.Ft[0][0].id.dec > self.id) and k <= self.id:
            return Chord_Node(res_id, res_hex, self.reps, as_max), True
        
        # is the succesor
        if self.id < k <= self.Ft[1][0].id.dec:
            return self.Ft[1]
        
        # is in the finger table
        less_than_me = False
        if k < self.id:
            less_than_me = True
            k += self.max_id

        for i in range(2, len(self.Ft)):
            if ((i == (len(self.Ft) - 1)) or (self.Ft[i][0].id.dec <= k < self.Ft[i + 1][0].id.dec)):
                if less_than_me and self.Ft[i][0].as_max:
                    num = self.Ft[i][0].id.dec - self.max_id
                    num_hex = hex(num)[2:]
                    return Chord_Node(num ,num_hex ,self.Ft[i][0].ip_list ,False), self.Ft[i][1]
                else:
                    return self.Ft[i]

    
    # endregion

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
    
    # Para enviar solo una cantidad de veces específica (si no hace falta luego borrar)
    def send_soft(self, ips, msg, req, port, try_count):
        response = None
        for _ in range(try_count):
            response = self.send_and_close(ips, msg, port)
            if not response:
                self.update_log(f'failed to send {req} to {ips}:{port}')
                sleep(2)
            else:
                break
        return response #####################################################
            
    # endregion

    # region Server

    def create_msg(**kwargs):
        '''
        Create a message.
        '''
        kwargs['type'] = protocols.CHORD_INTERNAL
        return json.dumps(kwargs)
    
    def update_log(self, entry):
        '''
        Update the log with an entry.
        '''
        with self.log_lock:
            if entry:
                self.log.append((entry ,str(datetime.now().time())))
        return
    
    def MaintainFt(self):
            '''
            Maintain the finger table.
            '''
            while(True):
                with self.Ft_lock:
                    if not self.Ft[0][1]:
                        self.get_reps(self.Ft[0][0])
                for i in range(1 ,len(self.Ft)):
                    current = self.id + 2**(i - 1)
                    who, mine = self.succ_who(current ,False)
                    if not mine:
                        current_hex = hex(current)[2:]
                        who = self.ask_succ(who.ip_list ,current_hex ,who.as_max)
                    with self.Ft_lock:
                        self.Ft[i] = (who,self.ip in who.ip_list)
                self.update_log()
                sleep(5)

    def start(self):
        '''
        Start the server.
        '''
        # Initialize thread for start server
        server_thread = Thread(target=self.start_server)##################################
        server_thread.start()

        ips = self.get_some_node()

        if not ips:
            self.update_log('First node to join the network')
            self.insert_as_first()
        else:
            self.update_log('Node to join the network')
            self.insert(ips)

        # Initialize thread for maintaining the finger table
        ft_thread = Thread(target=self.MaintainFt, daemon=True)
        ft_thread.start()

        try:
            insert_response = self.build_insert_response(self)
            self.send_soft(['127.0.0.1'], insert_response, "to_logger", protocols.PORT_GENERAL_LOGGER, 5)

            ##################################### NOTIFICAR AL TWITTER SERVER DE LA EXISTENCIA DE CHORD SERVER #################

            self.update_log('Node inserted in the network')

            server_thread.join()

        except Exception as e:
            self.update_log(f'Error starting the server: {e}')


    def start_server(self):
        self.server.bind(("0.0.0.0", self.port))
        self.server.listen()
        self.update_log(f'Server listening at port {self.port}')

        while True:
            conn, addr = self.server.accept()
            self.update_log(f'New connection from {addr}')

            request_thread = Thread(target=self.handle_request, args=(conn, addr)
            )
            request_thread.start()
    
    def handle_request(self, conn, addr):
        '''
        Handle a request.
        
        Params:
            conn: socket -> The socket connection.
            addr: str -> The address of the client.
        '''
        try:
            request = conn.recv(1024)
            parsed_request = self.parse_request(request)

            command = parsed_request['cmd']
            method = self.request_handler.get(command)

            if method:
                method(parsed_request, conn, addr)
            else:
                self.update_log(f'Command {command} not found')

        except Exception as e:
            self.update_log(f'Error in handle_request: {e}')

        finally:
            conn.close()

    def parse_request(self, request):
        '''
        Parse a request.

        Params:
            request: bytes -> The raw bytes received from the client.

        Returns:
            dict -> A dictionary containing the parsed command and its parameters.
        '''
        try:
            request_str = request.decode('utf-8')
            parsed_request = json.loads(request_str)
            
            if 'cmd' not in parsed_request:
                self.update_log("Missing 'cmd' in request")

            if 'id_hex' not in parsed_request:
                self.update_log("Missing 'id_hex' in request")

            if 'owner_ip' not in parsed_request:
                self.update_log("Missing 'owner_ip' in request")

            return parsed_request
        
        except Exception as e:
            self.update_log(f'Error in parse_request: {str(e)}')
            parsed_request = {}


    def get_some_node(self):
        '''
        Get some node info from the network.
        '''
        self.update_log('starting to send for (get_some_node)')
        msg_dict = {
            'type': protocols.CHORD ,
            'proto': protocols.NEW_LOGGER_REQUEST
        }
        text = json.dumps(msg_dict)
        response = self.send_til_success(self.entry_points ,text ,'register' , protocols.PORT_GENERAL_ENTRY)
        resp_dict = json.loads(response)
        return resp_dict['ip_loggers']
    
    def build_insert_response(self):
        '''
        Build the response to the logger.
        '''
        msg_dict = {
            'type': protocols.CHORD ,
            'proto': protocols.NEW_LOGGER_REQUEST,
            'sucesors': self.Ft[1][0].ip_list,
            'siblings':self.reps ,#########################################################################
            'chord_id': self.id_hex
        }
        return json.dumps(msg_dict)
    
    # endregion

    # region Handlers
    def ImYSucc_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the ImYSucc message.
        '''
        self.update_log('start receiving ImYSucc')
        res_hex = msg['id_hex']
        res_id = int(res_hex,16)
        as_max = False
        
        # If the new succ is the min, I'm the max
        if res_id < self.id:
            res_id += self.max_id
            res_hex = hex(res_id)[2:]
            as_max = True
        succ_node = None
        with self.Ft_lock:
            self.Ft[1] = (Chord_Node(res_id ,res_hex ,[msg['owner_ip']] ,as_max),False)
            succ_node = self.Ft[1][0]
        
        self.new_Succ(succ_node)
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end receiving ImYSucc')

    def new_Succ(self,succ_node):
        '''
        Update the successor of the node.
        '''
        msg = Chord_Server.create_msg(cmd = self.new_succ_cmd,node = str(succ_node))
        for rep in self.reps:
            if rep != self.ip:                
                self.send_soft([rep],msg,'new succ',self.port,5,have_recv=False)

    def ImYPrev_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the ImYPrev message.
        '''
        self.update_log('start receiving ImYPrev')
        
        busy = None
        with self.busy_lock:
            busy = self.busy
            if not self.busy:
                self.busy = True
        if busy:
            socket_client.send('Busy,none'.encode()) 
        else:
            result = None
            with self.Ft_lock:
                result = self.Ft[0][0]
            msg_id = int(msg['id_hex'],16)
            res_id = result.id.dec
            res_id_hex = result.id.hex
            res_as_max = result.as_max

            # Si el que se va a insertar es nuevo maximo
            if msg_id > self.id:
                res_id -= self.max_id
                res_id_hex = hex(res_id)[2:]
                res_as_max = False
            s_res = str(Chord_Node(res_id,res_id_hex,result.ip_list,res_as_max))

            # (Busy|Ok) ,id ,ip
            msg = json.dumps(['Ok',s_res])
            
            socket_client.send(msg.encode()) 
        socket_client.close()
        
        self.update_log('end receiving ImYPrev')

    def ImYRep_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the ImYRep message.
        '''
        self.update_log('start receiving ImYRep')
        busy = False
        
        with self.busy_lock:
            busy = self.busy
        if busy:
            
            socket_client.send('Busy,none,none'.encode())
        else:
            
            prev = None
            succ = None
            with self.Ft_lock:
                prev = self.Ft[0][0]
                succ = self.Ft[1][0]
            try:
                if msg['owner_ip'] not in self.reps:
                    self.reps.append(msg['owner_ip'])
            except Exception as e:
                print('----------')
                print(e)
                print(msg)
            
            s = json.dumps(['Ok',str(prev),str(succ),self.reps])
            socket_client.send(s.encode())
        socket_client.close()
        self.update_log('end receiving ImYRep')

    def get_succ_req_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the get_succ_req message.
        '''
        socket_client.send('Ok'.encode())
        socket_client.close()
        
        self.update_log(f'start receiving get_succ_req {msg["id_hex"]}')

        id = TwoBase(int(msg["id_hex"],16),msg['id_hex'])
        self.succ(id,msg['owner_ip'] ,msg['as_max'] ,msg['req_id'])
        self.update_log('end receiving get_succ_req')

    def get_succ_resp_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the get_succ_resp message.
        '''
        self.update_log('start receiving get_succ_resp')
        holder = self.state_storage.get_state(msg['req_id'])

        if holder is None:
            return
        holder.desired_data = Chord_Node.build_from_message(msg['node'])
        holder.hold_event.set()
        self.state_storage.delete_state(msg['req_id'])
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec get_succ_resp')

    def outside_handler(self ,msg ,socket_client ,addr):
        socket_client.close()
        
        self.update_log(f'start receiving outside_get {msg["id_hex"]}')
        
        holder : Thread_Holder = self.state_storage.insert_state()
        
        id = TwoBase(int(msg['id_hex'],16),msg['id_hex'] )

        while not holder.desired_data:
            mine = self.succ(id,self.ip ,False ,holder.id)
            self.update_log(f'me:{str(mine)}')
            
            if not mine:
                self.update_log('starting to wait')
                
                holder.hold_event.wait(5)
            else:
                holder.desired_data = Chord_Node(self.id ,self.id_hex ,self.reps ,False)
            if not holder.desired_data:
                self.update_log(f'failed to get succ of {msg["id_hex"]}')
                
        self.state_storage.delete_state(holder.id)
        self.update_log('responding to outside')
        
        self.response_to_outside(holder.desired_data.ip_list,msg['req_id'])

    def response_to_outside(self,ip_list,req_id):
        
        self.update_log('responding to outside')
        
        msg_dict = {
            'type': protocols.LOGGER ,
            'proto': protocols.CHORD_RESPONSE ,
            'IP':ip_list,
            'id_request':req_id
        }
        
        self.send_soft(['127.0.0.1'],json.dumps(msg_dict),'outside_resp',protocols.PORT_GENERAL_LOGGER,5,have_recv = False)

        self.update_log(f'end outside req')
    

    def new_rep_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the new_rep message.
        '''
        if msg['owner_ip'] not in self.reps:
            self.reps.append(msg['owner_ip'])
        socket_client.send('Ok'.encode())

    def new_rep(self,rep_node: Chord_Node):
    
        for rep in rep_node.ip_list:
            msg = Chord_Server.create_msg(cmd = self.new_rep_cmd, owner_ip = self.ip)
            self.send_soft([rep],msg,'new_rep',self.port,5)

    def new_prev_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the new_prev message.
        '''
        new_prev = Chord_Node.build_from_message(msg['node'])
        with self.Ft_lock:
            self.Ft[0] = (new_prev,False)
        socket_client.close()

    def new_succ_handler(self ,msg ,socket_client ,addr):
        '''
        Receive the new_succ message.
        '''
        new_succ = Chord_Node.build_from_message(msg['node'])
        with self.Ft_lock:
            self.Ft[1] = (new_succ,False)
        socket_client.close()

    def get_reps_handler(self ,msg ,socket_client ,addr):
        resp = json.dumps(self.reps)
        socket_client.send(resp.encode())
        socket_client.close()

    def confirm_new_prev_handler(self ,msg:dict ,socket_client ,addr):
        self.update_log('inside rec_confirm')
        res_id_hex = msg['id_hex']
        res_id = int(res_id_hex,16)
        res_as_max = False
        if res_id > self.id:
            res_id += self.max_id
            res_id_hex = hex(res_id)[2:]
            res_as_max = True
        prev_node = None
        with self.Ft_lock:
            self.Ft[0] = (Chord_Node(res_id ,res_id_hex ,[msg['owner_ip']] ,res_as_max),False)
            prev_node = self.Ft[0][0]
        
        with self.busy_lock:
            self.busy = False
        
        self.new_Prev(prev_node)
        
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('confirmed new prev')

    def new_Prev(self,prev_node):
        
        msg = Chord_Server.create_msg(cmd = self.new_prev_cmd,node = str(prev_node))
        for rep in self.reps:
            if rep != self.ip:
                self.send_soft([rep],msg,'new succ',self.port,5,have_recv=False)

    # endregion