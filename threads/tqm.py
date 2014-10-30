import Queue
"""
Thread Queue Manager.

A complex solution for managing thread interconnects
in a complex application using Python's Queues
"""

class TQM(object):
    """A root of TQM. Registers queues and so on.
    Registering and creating pipes isn't really threadsafe.
    
    This operates by two abstractions.
    
    A Writer is a Queue-like with only .put() and .put_nowait().
    A Reader is a Queue-like with only .get() and .get_nowait().
    These throw Queue.Empty on empty.
    """
    
    
    class Interface(object):
        """An interface returned if get_interface_for is called.
        All its methods have to result in a .put to the queue"""
        def __init__(self, queue):
            self.queue = queue
    
    class MultiWriter(object):
        """A fake write-only queue that posts messages to multiple queues"""
        def __init__(self, queuelist):
            self.queuelist = queuelist
            
        def put(self, item, block=False, timeout=None):
            for q in self.queuelist:
                q.put(item, block, timeout)
    
        def put_nowait(self, item):
            self.put(item, False)
    
    class IterableReader(object):
        """A wrapper around a Queue with additional property:
        you can iterate over it. It will return messages received, and terminate
        iteration when it has no more. You can use it like this:
        
            while not terminating: # main program loop
                for msg in myIterableReader:
                    process(msg)
                .. do other stuff ..
        """
        def __init__(self, queue):
            self.queue = queue
            
        def get(self, block=False, timeout=None):
            return self.queue.get(block, timeout)
        
        def get_nowait(self):
            return self.queue.get_nowait()
        
        def __iter__(self):
            return self

        def next(self):
            try:
                return self.queue.get_nowait()
            except Queue.Empty:
                raise StopIteration()
    
    def __init__(self):
        self.db = {}        # name => queue
        self.interfaces = {} # name => sugarcoat object
        
    def _get_queue_for(self, name):
        if name not in self.db:
            self.db[name] = Queue.Queue()
        return self.db[name]
            
    def register_interface(self, name, ifc):
        """
        @param ifc: interface class. An interface
            object will be created with target queue name
        @type ifc: class of TQM.Interface"""
        self.interfaces[name] = ifc(self._get_queue_for(name))
        
    def get_interface_for(self, name):
        return self.interfaces[name]
        
    def get_reader_for(self, name):
        return TQM.IterableReader(self._get_queue_for(name))
    
    def get_writer_for(self, name):
        return self._get_queue_for(name)
    
    def get_multiwriter(self, names):
        """@type names: sequence of names"""
        return TQM.MultiWriter([self._get_queue_for(x) for x in names])