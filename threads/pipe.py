import Queue

class Pipe(Queue.Queue):
    """Represents a bidirectional inter-thread queue.
    
    Essentially it is a Queue.Queue, so that .put elements
    appear in the other queue.
    
    This will contain cyclic references, so it should be 
    kinda persistent. 
    
    Call .close() to terminate that cyclic reference.
    """
    
    Empty = Queue.Empty
    
    def __init__(self):
        Queue.Queue.__init__(self)
        self.other_queue = None
        
    def put(self, item, block=True, timeout=None):
        Queue.Queue.put(self.other_queue, item, block, timeout)

def create_pipes():
    """Returns a pair (tuple) of Pipes connecting to each
    other"""    
    a = Pipe()
    b = Pipe()
    a.other_queue = b
    b.other_queue = a
    return a, b
    
    