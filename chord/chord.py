import socket
import threading
import sys
import time
import hashlib
from models.model import *

# Operation codes
FIND_SUCCESSOR = 1
FIND_PREDECESSOR = 2
GET_SUCCESSOR = 3
GET_PREDECESSOR = 4
NOTIFY = 5
CHECK_PREDECESSOR = 6
CLOSEST_PRECEDING_FINGER = 7

# Get an unique id for a node (SHA1 hash of the ip address)
def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(),16)

# Reference to a node in the Chord network
class ChordNodeReference:
    def __init__(self, id: int, ip: str, port: int = 8001):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port

    def _send_data(self, op: int, data: str = None) -> bytes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                s.sendall(f'{op},{data}'.encode('utf-8'))
                return s.recv(1024)
        except Exception as e:
            print(f"Error sending data: {e}")
            return b''

    def find_successor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_SUCCESSOR, str(id)).decode().split(',')
        return ChordNodeReference(int(response[0]), response[1], self.port)

    def find_predecessor(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(FIND_PREDECESSOR, str(id)).decode().split(',')
        return ChordNodeReference(int(response[0]), response[1], self.port)

    @property
    def succ(self) -> 'ChordNodeReference':
        response = self._send_data(GET_SUCCESSOR).decode().split(',')
        return ChordNodeReference(int(response[0]), response[1], self.port)

    @property
    def pred(self) -> 'ChordNodeReference':
        response = self._send_data(GET_PREDECESSOR).decode().split(',')
        return ChordNodeReference(int(response[0]), response[1], self.port)

    def notify(self, node: 'ChordNodeReference'):
        self._send_data(NOTIFY, f'{node.id},{node.ip}')

    def check_predecessor(self):
        self._send_data(CHECK_PREDECESSOR)

    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        response = self._send_data(CLOSEST_PRECEDING_FINGER, str(id)).decode().split(',')
        return ChordNodeReference(int(response[0]), response[1], self.port)

    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.port}'

    def __repr__(self) -> str:
        return str(self)


class ChordNode:
    def __init__(self, id: int, ip: str, port: int = 8001, m: int = 160):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.id, self.ip, self.port)
        self.succ = self.ref  # Initial successor is itself
        self.pred = None  # Initially no predecessor
        self.m = m  # Number of bits in the hash/key space
        self.finger = [self.ref] * self.m  # Finger table
        self.next = 0  # Finger table index to fix next

        threading.Thread(target=self.stabilize, daemon=True).start()  # Start stabilize thread
        threading.Thread(target=self.fix_fingers, daemon=True).start()  # Start fix fingers thread
        threading.Thread(target=self.check_predecessor, daemon=True).start()  # Start check predecessor thread
        threading.Thread(target=self.start_server, daemon=True).start()  # Start server thread
    
    def _inbetween(self, k: int, start: int, end: int) -> bool:
        """Check if k is in the interval (start, end]."""
        if start < end:
            return start < k <= end
        else:  # The interval wraps around 0
            return start < k or k <= end

    def find_succ(self, id: int) -> 'ChordNodeReference':
        node = self.find_pred(id)  # Find predecessor of id
        return node.succ  # Return successor of that node

    def find_pred(self, id: int) -> 'ChordNodeReference':
        node = self
        while not self._inbetween(id, node.id, node.succ.id):
            node = node.closest_preceding_finger(id)
        return node

    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        for i in range(self.m - 1, -1, -1):
            if self.finger[i] and self._inbetween(self.finger[i].id, self.id, id):
                return self.finger[i]
        return self.ref

    def join(self, node: 'ChordNodeReference'):
        """Join a Chord network using 'node' as an entry point."""
        if node:
            self.pred = None
            self.succ = node.find_successor(self.id)
            self.succ.notify(self.ref)
        else:
            self.succ = self.ref
            self.pred = None

    def stabilize(self):
        """Regular check for correct Chord structure."""
        while True:
            try:
                if self.succ.id != self.id:
                    print('stabilize')
                    x = self.succ.pred
                    if x.id != self.id:
                        print(x)
                        if x and self._inbetween(x.id, self.id, self.succ.id):
                            self.succ = x
                        self.succ.notify(self.ref)
            except Exception as e:
                print(f"Error in stabilize: {e}")

            print(f"successor : {self.succ} predecessor {self.pred}")
            time.sleep(10)

    def notify(self, node: 'ChordNodeReference'):
        if node.id == self.id:
            pass
        if not self.pred or self._inbetween(node.id, self.pred.id, self.id):
            self.pred = node

    def fix_fingers(self):
        while True:
            try:
                i = self.next
                start = (self.id + 2 ** i) % (2 ** self.m)
                self.finger[i] = self.find_successor(start)
                self.next = (self.next + 1) % self.m
            except Exception as e:
                print(f"Error in fix_fingers: {e}")
            time.sleep(10)



    def check_predecessor(self):
        while True:
            try:
                if self.pred:
                    self.pred.check_predecessor()
            except Exception as e:
                self.pred = None
            time.sleep(10)

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)##############################################################################

            while True:
                conn, addr = s.accept()
                print(f'new connection from {addr}' )

                data = conn.recv(1024).decode().split(',')

                data_resp = None
                option = int(data[0])

                if option == FIND_SUCCESSOR:
                    id = int(data[1])
                    data_resp = self.find_succ(id)
                elif option == FIND_PREDECESSOR:
                    id = int(data[1])
                    data_resp = self.find_pred(id)
                elif option == GET_SUCCESSOR:
                    data_resp = self.succ if self.succ else self.ref
                elif option == GET_PREDECESSOR:
                    data_resp = self.pred if self.pred else self.ref
                elif option == NOTIFY:
                    id = int(data[1])
                    ip = data[2]
                    self.notify(ChordNodeReference(id, ip, self.port))
                elif option == CHECK_PREDECESSOR:
                    pass
                elif option == CLOSEST_PRECEDING_FINGER:
                    id = int(data[1])
                    data_resp = self.closest_preceding_finger(id)

                if data_resp:
                    response = f'{data_resp.id},{data_resp.ip}'.encode()
                    conn.sendall(response)
                conn.close()

    def store_data(self, username, data):
        key = getShaRepr(username)
        target_node = self.find_successor(key)
        if target_node == self:
            # Store in local database
            with db.atomic():
                user, created = User.get_or_create(username=username)
                if isinstance(data, dict): 
                    #This means that the data is the user's info
                    for field, value in data.items():
                        setattr(user, field, value)
                    user.save()
                elif isinstance(data, Tweet):
                    Tweet.create(user=user, content=data.content)
                elif isinstance(data, Retweet):
                    Retweet.create(user=user, orig_user=data.orig_user, created_at=data.created_at, retweeted_at=data.retweeted_at)
                elif isinstance(data, Follow):
                    Follow.create(follower=user, following=data.following)
        else:
            # Forward to the appropriate node
            target_node.store_data(username, data)

    def verify_user(self, username):
        key = getShaRepr(username)
        target_node = self.find_successor(key)
        if target_node == self:
            user = User.get_or_none(User.username == username)
            return user is not None
        else:
            return target_node.verify_user
    
    def verify_password(self):
        key = getShaRepr(self.user.username)
        target_node = self.find_successor(key)
        if target_node == self:
            user = User.get_or_none(User.username == self.user.username)
            return user.password == self.user.password
        else:
            return target_node.verify_password()

    def retrieve_data(self, username, data_type=None):
        key = getShaRepr(username)
        target_node = self.find_successor(key)
        if target_node == self:
            # Retrieve from local database
            user = User.get_or_none(User.username == username)
            if user is None:
                return None ################################################ Throw an error message, do not return NONE
            if data_type is None:
                # Return all user data
                return {
                    'user': user,
                    'tweets': list(user.tweets), ########################### Check out if this works 
                    'retweets': list(user.retweets),
                    'following': list(Follow.select().where(Follow.follower == user)),
                    'followers': list(Follow.select().where(Follow.following == user.username))
                }
            elif data_type == 'user':
                return user
            elif data_type == 'tweets':
                return list(user.tweets)
            elif data_type == 'retweets':
                return list(user.retweets)
            elif data_type == 'following':
                return list(Follow.select().where(Follow.follower == user))
            elif data_type == 'followers':
                return list(Follow.select().where(Follow.following == user.username))
        else:
            # Forward request to the appropriate node
            return target_node.retrieve_data(username, data_type)
        
    def replicate_data(self, username, data, replication_factor=3): ###### Analize replication factor default value
        key = getShaRepr(username)
        nodes = [self]
        current = self
        for _ in range(replication_factor - 1):
            current = current.successor
            nodes.append(current)
        
        for node in nodes:
            node.store_data(username, data)

    def recover_data(self, failed_node):
        start_key = getShaRepr(failed_node.predecessor.username)
        end_key = getShaRepr(failed_node.username)
        
        # Iterate through local database and redistribute data
        for user in User.select():
            key = getShaRepr(user.username)
            if start_key < key <= end_key:
                user_data = self.retrieve_data(user.username)
                self.replicate_data(user.username, user_data)


###########################################################################################

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    id = getShaRepr(ip)
    node = ChordNode(id, ip)

    if len(sys.argv) >= 2:
        other_ip = sys.argv[1]
        id = getShaRepr(other_ip)
        node.join(ChordNodeReference(other_ip, other_ip, node.port))
    
    while True:
        pass
