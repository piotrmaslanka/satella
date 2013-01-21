from threading import Thread, Lock

class BaseThread(Thread):
    """Thread with internal termination flag"""
    def __init__(self, *args, **kwargs):
        self._terminating = False
        Thread.__init__(self, *args, **kwargs)

    def terminate(self):
        """Sets internal termination flag"""
        self._terminating = True


class Monitor(object):
    """
    Base utility class for creating monitors (the synchronization thingies!)
    """
    def __init__(self):
        """You need to invoke this at your constructor"""
        self.lock = Lock()

    @staticmethod    
    def protect(fun):
        """
        This is a decorator. Class method decorated with that will lock the 
        global lock of given instance, making it threadsafe. Depending on 
        usage pattern of your class and it's data semantics, your performance
        may vary
        """
        def monitored(*args, **kwargs):
            with args[0].lock:
                return fun(*args, **kwargs)
        return monitored