import threading
import time

array = [1, 2, 3]
lock = threading.Lock()

def use():
    while True:
        #lock=threading.Lock()
        with lock:  # Asegúrate de adquirir el candado antes de acceder al array
            print(array[0])
        time.sleep(1)  # Agregamos un pequeño retraso para evitar saturar la salida

def use2():
    while True:
        #lock2=threading.Lock()
        with lock:
            for i in range(0, 10000):
                array.append(i)
            print(array)  # Imprimimos el array después de modificarlo
            print("b")
        time.sleep(20)

# Crear hilos
t1 = threading.Thread(target=use)
t2 = threading.Thread(target=use2)

# Iniciar hilos
t1.start()
t2.start()
