from .proxy import Proxy


class HashableWrapper(Proxy):
    """
    A class that makes given objects hashable by their id, if the object is already not hashable.

    Also overrides __eq__

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

    def __eq__(self, other) -> bool:
        my_object = getattr(self, '_Proxy__obj')
        if isinstance(other, HashableWrapper):
            obj2 = getattr(other, '_Proxy__obj')
        else:
            obj2 = other
        return id(my_object) == id(obj2)
