import typing as tp

from .shared import get_attribute


def length_less_than(x, attribute: tp.Optional[str] = None) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is less than x

    :param x: value of x
    :param attribute: if given, then it will first try to access given attribute of v
    """
    def predicate(v):
        return len(get_attribute(v, attribute)) < x
    return predicate


def length_is(x, attribute: tp.Optional[str] = None) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is x

    :param x: value of x
    :param attribute: if given, then it will first try to access given attribute of v
    """
    def predicate(v):
        return len(get_attribute(v, attribute)) == x
    return predicate


def length_multiple_of(x, attribute: tp.Optional[str] = None) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is a multiple of x

    :param x: value of x
    :param attribute: if given, then it will first try to access given attribute of v
    """
    def predicate(v):
        return not (len(get_attribute(v, attribute)) % x)
    return predicate
