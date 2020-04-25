from .proxy import Proxy


class HashableWrapper(Proxy):
    """
    A class that makes given objects hashable by their id.

    Note that this class will return a proxy to the object, and not the object itself.

    Use like:

    >>> class NotHashable:
    >>>     def __init__(self, a):
    >>>         self.a = a
    >>> a = HashableWrapper(NotHashable(5))
    >>> assert a.a == 5
    >>> a.a = 4
    >>> assert a.a == 4
    """
    __slots__ = ()

    def __hash__(self):
        return hash(id(self))
