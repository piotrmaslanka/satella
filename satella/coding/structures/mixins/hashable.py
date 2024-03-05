import operator
import typing as tp
from abc import ABCMeta, abstractmethod


class HashableMixin:
    """
    Make a class hashable by its ID.

    Just remember to add the following to your class definition
    if you're overriding __eq__:

    >>> class MyClass(HashableMixin):
    >>>     __hash__ = HashableMixin.__hash__
    """
    __slots__ = ()

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other) -> bool:
        return id(self) == id(other)


class ComparableAndHashableBy(metaclass=ABCMeta):
    """
    A mix-in. Provides comparision (lt, gt, ge, le, eq) and hashing by a field of this class.
    Hashing is done by invoking hash() on the value of the field, and comparison is done by
    directly comparing given field's values.

    Example:

    >>> class Vector(ComparableAndHashableBy):
    >>>     _COMPARABLE_BY = 'length'
    >>>     @property
    >>>     def length(self):
    >>>         return 0
    >>>
    >>> assert Vector() > Vector()
    """
    __slots__ = ()

    @property
    @abstractmethod
    def _COMPARABLE_BY(self) -> str:  # pylint: disable=invalid-name
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


class ComparableAndHashableByInt(metaclass=ABCMeta):
    """
    A mix-in. Provides comparison (lt, gt, ge, le, eq) and hashing by __int__ of this class.
    """

    __slots__ = ()

    @abstractmethod
    def __int__(self) -> int:
        ...

    def __hash__(self):
        return hash(int(self))

    def __eq__(self, other: 'ComparableAndHashableByInt') -> bool:
        return int(self) == int(other)

    def __lt__(self, other: 'ComparableAndHashableByInt') -> bool:
        return int(self) < int(other)

    def __le__(self, other: 'ComparableAndHashableByInt') -> bool:
        return int(self) <= int(other)

    def __gt__(self, other: 'ComparableAndHashableByInt') -> bool:
        return int(self) > int(other)

    def __ge__(self, other: 'ComparableAndHashableByInt') -> bool:
        return int(self) >= int(other)


class ComparableAndHashableByStr(metaclass=ABCMeta):
    """
    A mix-in. Provides comparision (lt, gt, ge, le, eq) and hashing by __str__ of this class.
    Also, will make this class equal to strings that return the same value.
    """

    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        ...

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: 'ComparableAndHashableByInt') -> bool:
        return str(self) == str(other)

    def __lt__(self, other: 'ComparableAndHashableByInt') -> bool:
        return str(self) < str(other)

    def __le__(self, other: 'ComparableAndHashableByInt') -> bool:
        return str(self) <= str(other)

    def __gt__(self, other: 'ComparableAndHashableByInt') -> bool:
        return str(self) > str(other)

    def __ge__(self, other: 'ComparableAndHashableByInt') -> bool:
        return str(self) >= str(other)


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

    This will also check if the other value is an instance of this instance's class.

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
    def _HASH_FIELDS_TO_USE(self) -> tp.Union[str, tp.Sequence[str]]:  # pylint: disable=invalid-name
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
        return _generic_eq(self, other, False, operator.eq)

    def __ne__(self, other) -> bool:
        return _generic_eq(self, other, True, operator.ne)


def _generic_eq(self, other, truth, comparator):
    if not isinstance(other, type(self)):
        return truth

    cmpr_by = self._HASH_FIELDS_TO_USE      # pylint: disable=protected-access
    try:
        if isinstance(cmpr_by, str):
            return comparator(getattr(self, cmpr_by), getattr(other, cmpr_by))

        if any(getattr(self, field_name) != getattr(other, field_name) for field_name in cmpr_by):
            return truth
        return not truth
    except AttributeError:
        return truth
