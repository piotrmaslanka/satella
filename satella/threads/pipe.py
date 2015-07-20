import Queue

class Pipe(Queue.Queue):
    """Represents a bidirectional inter-thread queue.
    
    Essentially it is a Queue.Queue, so that .put elements
    appear in the other queue.
    
    This will contain cyclic references, so it should be 
    kinda persistent. 
    
    Call .close() to terminate that cyclic reference.
    
    Throws Queue.Empty where it makes sense. You can
    use Pipe.Empty - contains a handy shortcut to the same
    exception
    """
    
    Empty = Queue.Empty
    
    def __init__(self):
        Queue.Queue.__init__(self)
        self.other_queue = None
        
    def put(self, item, block=True, timeout=None):
        Queue.Queue.put(self.other_queue, item, block, timeout)

    def close(self):
        self.other_queue = None
        
def create_pipes(queue_for_a=None, queue_for_b=None):
    """Returns a pair (tuple - a, b) of Pipes connecting to each
    other
    
    @param queue_for_a: if defined, should be a Queue that a's .put()
    will send messages to
    @param queue_for_b: same as queue_for_a, but for b
    """    
    a = Pipe()
    b = Pipe()
    if queue_for_a == None:
        a.other_queue = b
    else:
        a.other_queue = queue_for_a
    if queue_for_b == None:
        b.other_queue = a
    else:
        b.other_queue = queue_for_a
    return a, b
    
    