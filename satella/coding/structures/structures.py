import functools
import operator
import typing as tp
from abc import ABCMeta, abstractmethod


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

    for this to work in your class
    """
    __slots__ = ()

    @property
    @abstractmethod
    def _HASH_FIELDS_TO_USE(self) -> tp.Sequence[str]:
        """
        Return the sequence of names of properties and attributes
        that will be used for __eq__ and __hash__
        """
        return ()

    def __hash__(self):
        return functools.reduce(operator.xor, (hash(getattr(self, field_name))
                                               for field_name in self._HASH_FIELDS_TO_USE))

    def __eq__(self, other: 'OmniHashableMixin') -> bool:
        """
        Note that this will only compare _HASH_FIELDS_TO_USE
        """

        def con(p):
            return tuple(getattr(p, field_name) for field_name in self._HASH_FIELDS_TO_USE)

        if isinstance(other, OmniHashableMixin):
            try:
                if con(self) == con(other):
                    return True
            except AttributeError:
                return False
        else:
            return super().__eq__(other)

    def __ne__(self, other: 'OmniHashableMixin') -> bool:
        return not self.__eq__(other)


class ReprableMixin:
    """
    A sane __repr__ default.

    This takes the values for the __repr__ from repr'ing list of fields defined as
    class property _REPR_FIELDS.

    Set an optional class property of _REPR_FULL_CLASSNAME for __repr__ to output the repr alongside the module name.

    Example:

    >>> class Test(ReprableMixin):
    >>>     _REPR_FIELDS = ('v', )
    >>>     def __init__(self, v, **kwargs):
    >>>         self.v = v
    >>>
    >>> assert repr(Test(2)) == "Test(2)"
    >>> assert repr(Test('2') == "Test('2')")
    """
    __slots__ = ()
    _REPR_FIELDS = ()

    def __repr__(self):
        fragments = []
        if hasattr(self, '_REPR_FULL_CLASSNAME'):
            if self._REPR_FULL_CLASSNAME:
                fragments = ['%s%s' % ((self.__class__.__module__ + '.')
                                       if self.__class__.__module__ != 'builtins' else '',
                                       self.__class__.__qualname__)]
        if not fragments:
            fragments = [self.__class__.__name__]
        fragments.append('(')
        arguments = []
        for field_name in self._REPR_FIELDS:
            arguments.append(repr(getattr(self, field_name)))
        fragments.append(', '.join(arguments))
        fragments.append(')')
        return ''.join(fragments)


