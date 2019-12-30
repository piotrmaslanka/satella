import functools
import threading

__all__ = [
    'Monitor', 'RMonitor'
]


class Monitor:
    """
    Base utility class for creating monitors (the synchronization thingies!)

    These are NOT re-entrant!

    Use it like that:

    >>> class MyProtectedObject(Monitor):
    >>>     def __init__(self, *args, **kwargs):
    >>>         Monitor.__init__(self)
    >>>         ... do your job ..

    >>>     @Monitor.synchronized
    >>>     def function_that_needs_mutual_exclusion(self):
    >>>         .. do your threadsafe jobs ..

    >>>     def function_that_partially_needs_protection(self):
    >>>         .. do your jobs ..
    >>>         with Monitor.acquire(self):
    >>>             .. do your threadsafe jobs ..
    """

    def __init__(self, obj=None):
        """You need to invoke this at your constructor
        You can also use it to release locks of other objects."""
        self._monitor_lock = threading.Lock()

    @staticmethod
    def synchronized(fun):
        """
        This is a decorator. Class method decorated with that will lock the
        global lock of given instance, making it threadsafe. Depending on
        usage pattern of your class and it's data semantics, your performance
        may vary
        """

        @functools.wraps(fun)
        def monitored(*args, **kwargs):
            # noinspection PyProtectedMember
            with args[0]._monitor_lock:
                return fun(*args, **kwargs)

        return monitored

    class release:
        """
        Returns a context manager object that can release another object
        as long as that object is a monitor.

        Consider foo, which is a monitor. You have a protected function,
        but you feel that you can release it for a while as it would
        improve parallelism. You can use it as such:

        >>> @Monitor.synchronized
        >>> def protected_function(self):
        >>>     .. do some stuff that needs mutual exclusion ..
        >>>     with Monitor.release(self):
        >>>         .. do some I/O that doesn't need mutual exclusion ..
        >>>     .. back to protected stuff ..
        """

        def __init__(self, foo: 'Monitor'):
            self.foo = foo

        def __enter__(self):
            # noinspection PyProtectedMember
            self.foo._monitor_lock.release()

        def __exit__(self, e1, e2, e3):
            # noinspection PyProtectedMember
            self.foo._monitor_lock.acquire()
            return False

    class acquire:
        """
        Returns a context manager object that can lock another object,
        as long as that object is a monitor.

        Consider foo, which is a monitor. If you needed to lock it from
        outside, you would do:

        >>> with Monitor.acquire(foo):
        >>>     .. do operations on foo that need mutual exclusion ..
        """

        def __init__(self, foo: 'Monitor'):
            self.foo = foo

        def __enter__(self):
            # noinspection PyProtectedMember
            self.foo._monitor_lock.acquire()

        def __exit__(self, e1, e2, e3):
            # noinspection PyProtectedMember
            self.foo._monitor_lock.release()
            return False


class RMonitor(Monitor):
    """
    Monitor, but using an reentrant lock instead of a normal one
    """

    def __init__(self):
        # todo refactor so that a Lock is not created uselessly
        super(RMonitor, self).__init__()
        self._monitor_lock = threading.RLock()
