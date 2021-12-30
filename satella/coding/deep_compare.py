import enum


class InequalityReason(enum.IntEnum):
    NOT_EQUAL = 0  #: direct eq yielded not equal
    LENGTH_MISMATCH = 1  #: length didn't match
    KEY_NOT_FOUND = 2  #: key given as obj1 was not found


class Inequal(Exception):
    """
    An exception raised by :meth:`~satella.coding.deep_compare` if two objects don't match

    :ivar obj1: first object that was not equal, or key name
    :ivar obj2: second object that was not equal, or None
    :ivar reason: (:class:`~satella.coding.InequalityReason`) reason for inequality
    """

    def __init__(self, obj1, obj2, reason: InequalityReason):
        self.obj1 = obj1
        self.obj2 = obj2
        self.reason = reason


def assert_equal(a, b):
    """
    Assert that two values are equal. If not, an :class:`satella.coding.Inequality` exception
    will be thrown.

    Objects are tried to compare using it's :code:`__eq__`.

    :param a: first value to compare
    :param b: second value to compare
    :raises Inequal: objects were not equal
    """
    if isinstance(a, (int, float, str, bytes, bytearray, type(None))):
        if a != b:
            raise Inequal(a, b, InequalityReason.NOT_EQUAL)
        return
    elif isinstance(a, (set, frozenset)):
        if len(a) != len(b):
            raise Inequal(a, b, InequalityReason.LENGTH_MISMATCH)
        if a != b:
            raise Inequal(a, b, InequalityReason.LENGTH_MISMATCH)
    elif isinstance(a, (list, tuple)):
        if len(a) != len(b):
            raise Inequal(a, b, InequalityReason.LENGTH_MISMATCH)
        for c, d in zip(a, b):
            assert_equal(c, d)
    elif isinstance(a, dict):
        if len(a) != len(b):
            raise Inequal(a, b, InequalityReason.LENGTH_MISMATCH)
        for key in a.keys():
            if key not in b:
                raise Inequal(key, None, InequalityReason.KEY_NOT_FOUND)
            assert_equal(a[key], b[key])
    else:
        try:
            if a == b:
                return
            raise Inequal(a, b, InequalityReason.NOT_EQUAL)
        except TypeError:
            pass
