from satella.coding.typing import Number


class Vector(tuple):
    """
    A tuple that allows place-wise addition and subtraction of it's entries, and also
    tuple-times-float operations

    Ie.

    >>> a = Vector((2, 3))
    >>> b = Vector((1, 2))
    >>> assert a-b == Vector((1, 1))
    >>> assert a*2 == Vector((4, 6))
    """

    def __add__(self, other: 'Vector') -> 'Vector':
        result = []
        for a, b in zip(self, other):
            result.append(a + b)
        return Vector(result)

    def __sub__(self, other: 'Vector') -> 'Vector':
        result = []
        for a, b in zip(self, other):
            result.append(a - b)
        return Vector(result)

    __iadd__ = __add__
    __isub__ = __sub__

    def __mul__(self, other: Number) -> 'Vector':
        result = []
        for a in self:
            result.append(a * other)
        return Vector(result)

    def __truediv__(self, other: Number) -> 'Vector':
        result = []
        for a in self:
            result.append(a / other)
        return Vector(result)

    __imul__ = __mul__
    __itruediv__ = __truediv__
