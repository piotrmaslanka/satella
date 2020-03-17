




def HashableWrapper(obj):
    """
    A decorator that makes given objects hashable by their id.

    Use like:

    >>> class NotHashable:
    >>>     def __init__(self, a):
    >>>         self.a = a
    >>> a = HashableWrapper(NotHashable(5))
    >>> assert a.a == 5
    >>> a.a = 4
    >>> assert a.a == 4
    """
    if not hasattr(obj, '__hash__'):
        obj.__hash__ = lambda self: hash(id(self))
    return obj
