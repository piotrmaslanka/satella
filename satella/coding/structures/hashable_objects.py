from .proxy import Proxy


class HashableWrapper(Proxy):
    """
    A class that makes given objects hashable by their id, if the object is already not hashable.

    Note that this class will return a proxy to the object, and not the object itself.

    Use like:

    >>> a = {1:2, 3:4}
    >>> a = HashableWrapper(a)
    >>> hash(a)
    """
    __slots__ = ()

    def __hash__(self):
        my_object = getattr(self, '_Proxy__obj')
        try:
            return hash(my_object)
        except TypeError:
            return hash(id(my_object))
