import collections
import copy

import threading
import typing as tp

from ..decorators import wraps

__all__ = [
    'Monitor', 'RMonitor', 'MonitorDict', 'MonitorList'
]

K, V, T = tp.TypeVar('K'), tp.TypeVar('V'), tp.TypeVar('T')



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
    >>>         .. do your jobs ..
    >>>         with self:
    >>>             .. do your threadsafe jobs ..
    """
    __slots__ = ('_monitor_lock',)

    def __enter__(self):
        self._monitor_lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._monitor_lock.release()
        return False

    def __init__(self):
        """You need to invoke this at your constructor
        You can also use it to release locks of other objects."""
        self._monitor_lock = threading.Lock()  # type: threading.Lock

    @staticmethod
    def synchronized(fun):
        """
        This is a decorator. Class method decorated with that will lock the
        global lock of given instance, making it threadsafe. Depending on
        usage pattern of your class and it's data semantics, your performance
        may vary
        """

        @wraps(fun)
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
        __slots__ = ('foo', )

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
        __slots__ = ('foo', )

        def __init__(self, foo: 'Monitor'):
            self.foo = foo

        def __enter__(self):
            # noinspection PyProtectedMember
            self.foo._monitor_lock.acquire()

        def __exit__(self, e1, e2, e3):
            # noinspection PyProtectedMember
            self.foo._monitor_lock.release()
            return False

    @classmethod
    def synchronize_on(cls, monitor):
        """
        A decorator for locking on non-self Monitor objects

        Use it like:

        >>> class MasterClass(Monitor):
        >>>     def get_object(self):
        >>>         class SlaveClass:
        >>>             @Monitor.synchronize_on(self)
        >>>             def get_object(self2):
        >>>                 ...
        >>>         return SlaveClass
        """

        def outer(fun):
            @wraps(fun)
            def inner(*args, **kwargs):
                with cls.acquire(monitor):
                    return fun(*args, **kwargs)

            return inner

        return outer


class RMonitor(Monitor):
    """
    Monitor, but using an reentrant lock instead of a normal one
    """
    __slots__ = ()

    def __init__(self):
        self._monitor_lock = threading.RLock()  # type: threading.RLock


class MonitorList(tp.Generic[T], collections.UserList, Monitor):
    """A list that is also a monitor"""

    def __init__(self, *args):
        collections.UserList.__init__(self, *args)
        Monitor.__init__(self)

    def __copy__(self):
        return MonitorList(copy.copy(self.data))

    def __deepcopy__(self, memo):
        return MonitorList(copy.deepcopy(self.data, memo))

    def __getitem__(self, item: tp.Union[slice, int]) -> T:
        return self.data[item]

    def __setitem__(self, key: int, value: T) -> None:
        self.data[key] = value

    def __delitem__(self, key: tp.Union[slice, int]) -> None:
        del self.data[key]


class MonitorDict(tp.Generic[K, V], collections.UserDict, Monitor):
    """A dict that is also a monitor"""

    def __init__(self, *args, **kwargs):
        collections.UserDict.__init__(self, *args, **kwargs)
        Monitor.__init__(self)

    def __getitem__(self, item: K) -> V:
        return self.data[item]

    def __setitem__(self, key: K, value: V) -> None:
        self.data[key] = value

    def __delitem__(self, key: K) -> None:
        del self.data[key]

    def __copy__(self):
        return MonitorDict(copy.copy(self.data))

    def __deepcopy__(self, memo):
        return MonitorDict(copy.deepcopy(self.data, memo))
