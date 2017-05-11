# coding=UTF-8
"""
Just useful objects to make your coding nicer every day
"""
from __future__ import print_function, absolute_import, division
import functools
import six
import threading


class Monitor(object):
    """
    Base utility class for creating monitors (the synchronization thingies!)

    These are NOT re-entrant!

    Use it like that:

        class MyProtectedObject(Monitor):
            def __init__(self, *args, **kwargs):
                Monitor.__init__(self)
                ... do your job ..

            @Monitor.synchronized
            def function_that_needs_mutual_exclusion(self):
                .. do your threadsafe jobs ..

            def function_that_partially_needs_protection(self):
                .. do your jobs ..
                with Monitor.acquire(self):
                    .. do your threadsafe jobs ..
    """

    def __init__(self):
        """You need to invoke this at your constructor"""
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

        @Monitor.synchronized
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


class RMonitor(Monitor):
    """
    Monitor, but using an reentrant lock instead of a normal one
    """

    def __init__(self):
        #todo refactor so that a Lock is not created uselessly
        super(RMonitor, self).__init__()
        self._monitor_lock = threading.RLock()


class CallableGroup(object):
    """
    This behaves like a function, but allows to add other functions to call
    when invoked, eg.

        c1 = Callable()

        c1.add(foo)
        c1.add(bar)

        c1(2, 3)

    Now both foo and bar will be called with arguments (2, 3). Their exceptions
    will be propagated.

    """
    # todo not threadsafe with oneshots

    def __init__(self, gather=False, swallow_exceptions=False):
        """
        :param gather: if True, results from all callables will be gathered
                       into a list and returned from __call__
        :param swallow_exceptions: if True, exceptions from callables will be
                                   silently ignored. If gather is set,
                                   result will be the exception instance
        """
        self.callables = [] # tuple of (callable, oneshot)
        self.gather = gather
        self.swallow_exceptions = swallow_exceptions

    def add(self, callable, oneshot=False):
        """
        :param oneshot: if True, callable will be unregistered after single call
        """
        self.callables.append((callable, oneshot))

    def __call__(self, *args, **kwargs):
        """
        Run the callable. All registered callables will be called with
        passed arguments, so they should have the same arity.

        If callables raise, it will be passed through.

        :return: list of results if gather was set, else None
        """
        clbl = self.callables       # for moar thread safety
        self.callables = []

        if self.gather:
            results = []

        for callable, oneshot in clbl:
            try:
                q = callable(*args, **kwargs)
            except Exception as e:
                if not self.swallow_exceptions:
                    raise   # re-raise
                q = e

            if self.gather:
                results.append(q)

            if not oneshot:
                self.callables.append((callable, oneshot))

        if self.gather:
            return results
