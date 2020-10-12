import enum


class ComparableEnum(enum.Enum):
    """
    An enum whose compare will try to convert value you compare it against
    to it's instance. Handly for writing code like:

    >>> a = 'test'
    >>> class Enum(ComparableEnum):
    >>>     A = 'test'
    >>> assert Enum.A == a
    """
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return self.__class__(other) == self
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
