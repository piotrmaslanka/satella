import typing as tp
from abc import ABCMeta, abstractmethod

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


class OmniHashableMixin(metaclass=ABCMeta):
    """
    A mix-in. Provides hashing and equal comparison for your own class using specified fields.

    Example of use:

    >>> class Point2D(OmniHashableMixin):
    >>>    _HASH_FIELDS_TO_USE = ['x', 'y']
    >>>    def __init__(self, x, y):
    >>>        ...

    and now class Point2D has defined __hash__ and __eq__ by these fields.
    Do everything in your power to make specified fields immutable, as mutating them will result
    in a different hash.

    Note that if you're explicitly providing __eq__ in your child class, you will be required to
    insert:

    >>>     __hash__ = OmniHashableMixin.__hash__
.
    for this to work in your class.

    This will attempt to obtain hash value of each specified field and xor them together.
    If it encounters a value whose hash() TypeErrors, it will try to iterate over it and
    calculate the value from the iterables. So this will happily consume even dicts and sets.

    Just take care not to modify them!
    """
    __slots__ = ()

    @property
    @abstractmethod
    def _HASH_FIELDS_TO_USE(self) -> tp.List[str]:
        """Return the names of properties that will be used for __eq__ and __hash__"""
        return []

    def __hash__(self):
        tot_hash = 0
        for field_name in self._HASH_FIELDS_TO_USE:
            value = getattr(self, field_name)
            try:
                tot_hash ^= hash(value)
            except TypeError:
                try:
                    items = value.items()
                except AttributeError:  # not a dict
                    items = value

                try:
                    for elem in items:
                        tot_hash ^= hash(elem)
                except TypeError:   # not an iterable
                    raise TypeError('Cannot calculate the hash from field %s' % (field_name, ))
        return tot_hash

    def __eq__(self, other: 'OmniHashableMixin') -> bool:
        """
        Note that this will only compare _HASH_FIELDS_TO_USE
        """

        def con(p):
            return [getattr(p, field_name) for field_name in self._HASH_FIELDS_TO_USE]

        if con(self) == con(other):
            return True

        if not isinstance(other, OmniHashableMixin):
            return str(self) == str(other)
        else:
            return False

    def __ne__(self, other: 'OmniHashableMixin') -> bool:
        return not self.__eq__(other)