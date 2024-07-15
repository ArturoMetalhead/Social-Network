from chord.chord import *
from models.model import *
import json

node = ChordNode(1, 'localhost')
node2 = ChordNode(2, 'localhost', 8002)
node3 = ChordNode(3, 'localhost', 8003)
node4 = ChordNode(4, 'localhost', 8004)


# node.join(node2)
# node2.join(node3)
# node3.join(node4)

node.join(ChordNodeReference(2, 'localhost', 8002))
node2.join(ChordNodeReference(3, 'localhost', 8003))
node3.join(ChordNodeReference(4, 'localhost', 8004))

#initialize_db(node)

#user = User("lala", "lala1", "lala@gmail.com")
user = {
    'username': 'lala',
    'password': 'lala1',
    'email': 'lala@gmail.com'
}

def convert_data(data):
    sdata = str(data)
    cdata = sdata.replace(',', ';')
    return cdata

# user=json.dumps({
#     'username': 'lala',
#     'password': 'lala1',
#     'email': 'lala@gmail.com'
# }).encode()
#user = User("lala", "lala1", "lala@gmail.com")
node.store_data('lala',user)
print(node.verify_user('lala'))