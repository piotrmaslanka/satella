import enum


class ComparableEnum(enum.Enum):
    """
    An enum whose compare will try to convert value you compare it against
    to it's instance. Handly for writing code like:

    >>> a = 'test'
    >>> class Enum(ComparableEnum):
    >>>     A = 'test'
    >>> assert Enum.A == a

    Comparison order doesn't matter, so either are True:

    >>> Enum.A == 'test'
    >>> 'test' == Enum.A

    Note, however, that following won't work:

    >>> 'test' in (Enum.A, )

    You can even compare enums across classes

    >>> class A(ComparableEnum):
    >>>     A = 1
    >>> class B(ComparableEnum):
    >>>     A = 1
    >>> assert A.A == B.A
    """

    def __eq__(self, other) -> bool:
        if isinstance(other, enum.Enum) and not isinstance(other, self.__class__):
            other = other.value

        if not isinstance(other, self.__class__):
            try:
                return self.__class__(other) == self
            except ValueError:      # other is not a correct member of this class!
                return False
        else:
            return super().__eq__(other)


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
    as hashability.

    It it has an int() method, it's fair game as comparison argument for this class.
    """

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: 'ComparableIntEnum') -> bool:
        if isinstance(other, (int, float)):
            return self.value < other
        return self.value < int(other)

    def __le__(self, other: 'ComparableIntEnum') -> bool:
        if isinstance(other, (int, float)):
            return self.value <= other
        return self.value <= int(other)

    def __gt__(self, other: 'ComparableIntEnum') -> bool:
        if isinstance(other, (int, float)):
            return self.value > other
        return self.value > int(other)

    def __ge__(self, other: 'ComparableIntEnum') -> bool:
        if isinstance(other, (int, float)):
            return self.value >= other
        return self.value >= int(other)

    def __eq__(self, other: 'ComparableIntEnum') -> bool:
        if isinstance(other, (int, float)):
            return self.value == other
        return self.value == int(other)
