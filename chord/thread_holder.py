from threading import Event

class Thread_Holder():
    """
    Class that holds a thread and a desired data.
    """
    def __init__(self, id: int, hold_event = None):
        self.id = id
        self.hold_event = None
        if not hold_event:
            self.hold_event = Event()
        else:
            self.hold_event = hold_event
        self.desired_data = None