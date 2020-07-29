import enum
import typing as tp
from abc import ABCMeta, abstractmethod


class HashableIntEnum(enum.IntEnum):
    """
    An enum.IntEnum that implements hashability, stemming from it's values, as well
    as hashability
    """

    def __hash__(self) -> int:
        return hash(self.value)


class ComparableIntEnum(HashableIntEnum):
    """
    An enum.IntEnum that implements comparision, stemming from it's values, as well
    as hashability
    """

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: 'ComparableIntEnum') -> bool:
        return self.value < other.value

    def __le__(self, other: 'ComparableIntEnum') -> bool:
        return self.value <= other.value

    def __gt__(self, other: 'ComparableIntEnum') -> bool:
        return self.value > other.value

    def __ge__(self, other: 'ComparableIntEnum') -> bool:
        return self.value >= other.value

    def __eq__(self, other: 'ComparableIntEnum') -> bool:
        return self.value == other.value


class StrEqHashableMixin(metaclass=ABCMeta):
    """
    A mix-in that outfits your class with an __eq__ and __hash__ operator that take
    their values from __str__ representation of your class.
    """
    __slots__ = ()

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    @abstractmethod
    def __str__(self) -> str:
        pass


class ComparableAndHashableBy(metaclass=ABCMeta):
    """
    A mix-in. Provides comparision (lt, gt, ge, le, eq) and hashing by a field of this class.

    Example:

    >>> class Vector(ComparableAndHashableBy):
    >>>     _COMPARABLE_BY = 'length'
    >>>     @property
    >>>     def length(self):
    >>>         ...
    >>>
    >>> assert Vector() > Vector()
    """

    @property
    @abstractmethod
    def _COMPARABLE_BY(self) -> str:
        """
        Return the sequence of names of properties and attributes
        that will be used for __eq__ and __hash__
        """
        return ''

    def __hash__(self):
        return hash(getattr(self, self._COMPARABLE_BY))

    def __eq__(self, other: 'ComparableAndHashableBy') -> bool:
        return getattr(self, self._COMPARABLE_BY) == getattr(other, other._COMPARABLE_BY)

    def __lt__(self, other: 'ComparableAndHashableBy') -> bool:
        return getattr(self, self._COMPARABLE_BY) < getattr(other, other._COMPARABLE_BY)

    def __le__(self, other: 'ComparableAndHashableBy') -> bool:
        return getattr(self, self._COMPARABLE_BY) <= getattr(other, other._COMPARABLE_BY)

    def __gt__(self, other: 'ComparableAndHashableBy') -> bool:
        return getattr(self, self._COMPARABLE_BY) > getattr(other, other._COMPARABLE_BY)

    def __ge__(self, other: 'ComparableAndHashableBy') -> bool:
        return getattr(self, self._COMPARABLE_BY) >= getattr(other, other._COMPARABLE_BY)


class OmniHashableMixin(metaclass=ABCMeta):
    """
    A mix-in. Provides hashing and equal comparison for your own class using specified fields.

    Example of use:

    >>> class Point2D(OmniHashableMixin):
    >>>    _HASH_FIELDS_TO_USE = ('x', 'y')
    >>>    def __init__(self, x, y):
    >>>        ...

    and now class Point2D has defined __hash__ and __eq__ by these fields.
    Do everything in your power to make specified fields immutable, as mutating them will result
    in a different hash.

    _HASH_FIELDS_TO_USE can be also a single string, in this case a single field called by this
    name will be taken.

    Note that if you're explicitly providing __eq__ in your child class, you will be required to
    insert:

    >>>     __hash__ = OmniHashableMixin.__hash__

    for this to work in your class
    """
    __slots__ = ()

    @property
    @abstractmethod
    def _HASH_FIELDS_TO_USE(self) -> tp.Tuple[str]:
        """
        Return the sequence of names of properties and attributes
        that will be used for __eq__ and __hash__
        """
        return ()

    def __hash__(self) -> int:
        xor = 0
        cmpr_by = self._HASH_FIELDS_TO_USE
        if isinstance(cmpr_by, str):
            return hash(getattr(self, cmpr_by))

        for field_name in cmpr_by:
            xor ^= hash(getattr(self, field_name))
        return xor

    def __eq__(self, other) -> bool:
        """
        Note that this will only compare _HASH_FIELDS_TO_USE
        """
        if isinstance(other, OmniHashableMixin):
            cmpr_by = self._HASH_FIELDS_TO_USE

            if isinstance(cmpr_by, str):
                return getattr(self, cmpr_by) == getattr(other, cmpr_by)

            for field_name in self._HASH_FIELDS_TO_USE:
                if getattr(self, field_name) != getattr(other, field_name):
                    return False
            return True
        else:
            return super().__eq__(other)

    def __ne__(self, other) -> bool:
        if isinstance(other, OmniHashableMixin):
            cmpr_by = self._HASH_FIELDS_TO_USE

            if isinstance(cmpr_by, str):
                return getattr(self, cmpr_by) != getattr(other, cmpr_by)

            for field_name in cmpr_by:
                if getattr(self, field_name) != getattr(other, field_name):
                    return True
            return False
        else:
            return super().__ne__(other)


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
        if getattr(self, '_REPR_FULL_CLASSNAME', False):
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
