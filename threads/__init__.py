from threading import Thread, Lock

class BaseThread(Thread):
    """Thread with internal termination flag"""
    def __init__(self, *args, **kwargs):
        self._terminating = False
        Thread.__init__(self, *args, **kwargs)

    def terminate(self):
        """Sets internal termination flag"""
        self._terminating = True
        return self

    def start(self):
        Thread.start(self)
        return self

class Monitor(object):
    """
    Base utility class for creating monitors (the synchronization thingies!)

    Use it like that:

        class MyProtectedObject(Monitor):
            def __init__(self, *args, **kwargs):
                Monitor.__init__(self)
                ... do your job ..

            @Monitor.protect
            def function_that_needs_mutual_exclusion(self):
                .. do your threadsafe jobs ..

            def function_that_partially_needs_protection(self):
                .. do your jobs ..
                with Monitor.acquire(self):
                    .. do your threadsafe jobs ..
    """
    def __init__(self):
        """You need to invoke this at your constructor"""
        self._monitor_lock = Lock()

    @staticmethod    
    def protect(fun):
        """
        This is a decorator. Class method decorated with that will lock the 
        global lock of given instance, making it threadsafe. Depending on 
        usage pattern of your class and it's data semantics, your performance
        may vary
        """
        def monitored(*args, **kwargs):
            with args[0]._monitor_lock:
                return fun(*args, **kwargs)
        return monitored


    class release(object):
        """
        Returns a context manager object that can release another object
        as long as that object is a monitor.

        Consider foo, which is a monitor. You have a protected function,
        but you feel that you can release it for a while as it would
        improve parallelism. You can use it as such:


        @Monitor.protect
        def protected_function(self):
            .. do some stuff that needs mutual exclusion ..
            with Monitor.release(self):
                .. do some I/O that doesn't need mutual exclusion ..
            .. back to protected stuff ..

        """
        def __init__(self, foo):
            self.foo = foo

        def __enter__(self):
            self.foo._monitor_lock.release()

        def __exit__(self, e1, e2, e3):
            self.foo._monitor_lock.acquire()
            return False


    class acquire(object):
        """
        Returns a context manager object that can lock another object,
        as long as that object is a monitor.

        Consider foo, which is a monitor. If you needed to lock it from
        outside, you would do:

            with Monitor.acquire(foo):
                .. do operations on foo that need mutual exclusion ..
        """
        def __init__(self, foo):
            self.foo = foo

        def __enter__(self):
            self.foo._monitor_lock.acquire()

        def __exit__(self, e1, e2, e3):
            self.foo._monitor_lock.release()
            return False
