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
    def __init__(self):
        self.lock = Lock()

    @staticmethod    
    def protect(fun):
        def monitored(*args, **kwargs):
            with args[0].lock:
                return fun(*args, **kwargs)
        return monitored