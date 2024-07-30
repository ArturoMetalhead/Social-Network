from threading import Lock

def gen_int_numbers():
    """
    Generator that yields integers starting from 0.
    """
    i = 0
    while True:
        yield i
        i+=1

class Number_Assigment():
    """
    Class that assigns unique integers to objects.
    """
    def __init__(self):
        self.free_ids = []
        self.iter = gen_int_numbers()
        self.lock = Lock()

    def get_id(self):
        """
        Get a new unique integer.
        """
        new_id = None
        with self.lock:
            if self.free_ids:
                new_id = self.free_ids.pop()
            else:
                new_id = next(self.iter)
        return new_id
    
    def free_id(self, id):
        """
        Free an integer so it can be reused.
        """
        with self.lock:
            self.free_ids.append(id)