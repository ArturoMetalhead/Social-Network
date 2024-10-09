import unittest
from unittest.mock import patch, Mock
from chord_server import Chord_Server, Chord_Node  # Importa la clase ChordServer
from threading import Thread
from time import sleep, time

class TestChordServer(unittest.TestCase):

    def setUp(self):
        self.server = Chord_Server(DHT_name="TestNetwork", port=5000, disable_log=False)

    def test_insert_as_first(self):
        # Verificar que se inserta correctamente como primer nodo
        self.server.insert_as_first()
        self.assertEqual(self.server.Ft[0][0].id.dec, self.server.id)
        self.assertTrue(self.server.Ft[0][0].as_max)

    def test_insert_new_node(self):
        # Simular la respuesta del nodo sucesor
        with patch.object(self.server, 'ImYPrev', return_value=(True, Mock())):
            with patch.object(self.server, 'ImYSucc', return_value=None):
                with patch.object(self.server, 'confirm_new_prev', return_value=None):
                    self.server.insert_new_node(["192.168.1.1"], Chord_Node("12345", "12345", ["192.168.1.1"], False))
        
        # Verificar que se actualiza correctamente la tabla de finger
        self.assertEqual(self.server.Ft[0][0].id.dec, self.server.id)
        self.assertTrue(self.server.Ft[0][0].as_max)

    def test_insert_rep_node(self):
       
        # Simular la respuesta del nodo replicado
        with patch.object(self.server, 'ImYRep', return_value=(True, Mock(), Mock(), ["192.168.1.2"])):
            self.server.insert_rep(Chord_Node("12345", "12345", ["192.168.1.2"], False))
        
        # Verificar que se actualiza correctamente la lista de replicados
        self.assertIn("192.168.1.2", self.server.reps)

# if __name__ == '__main__':
#     unittest.main()

# server = Chord_Server(DHT_name="Test", port = 5000, disable_log=False)
# server.insert_as_first()
# print(server.Ft[0][0].id.dec)
# print(server.id)

def simulate_node_insertion():
    server1 = Chord_Server(DHT_name="Node1", port=5000, ip='127.0.0.2', disable_log=False)
    sleep(2)
    thread1 = Thread(target=server1.start)
    thread1.start()
    print(server1.ip)


    sleep(10)

    #server1.insert_as_first()

    server2 = Chord_Server(DHT_name="Node2", port=5000, ip='127.0.0.3',disable_log=False, entry_points=[server1.ip])
    sleep(2)
    print(server2.ip)
    thread2 = Thread(target=server2.start)
    thread2.start()
    #server2.start()

    # Simula la inserción de nodos
    
    #server2.insert([server1.ip])

    # Verifica el estado de la red
    # for i in range(len(server1.Ft)):
    #     print("Finger Table of Node 1:", server1.Ft[i][0])
    
    
    inicio = time()
    while server2.Ft[0] == None:
        #print("SIGUE SIENDO NONE AFUERA LA FT DE LOS COJONES")
        pass
    fin = time()
    print(fin - inicio)
    for i in range(len(server2.Ft)):
        print("Finger Table of Node 2:", server2.Ft[i][0])

simulate_node_insertion()
