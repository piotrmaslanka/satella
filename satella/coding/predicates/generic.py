import typing as tp


def one_of(*args) -> tp.Callable[[tp.Any], bool]:
    """
    Return a predicate that will return True if passed value equals to one of the arguments

    :param args: a list of arguments on which the predicate will return True
    :param attribute: if given, then it will first try to access given attribute of v
    """
    def predicate(v):
        return v in args
    return predicate


def _is_not_none(v):
    return v is not None


def is_not_none():
    """
    Return a predicate that will return True if passed element is not None
    """
    return _is_not_none


def has_attr(x):
    """
    Build a predicate that returns True if passed element has attribute x
    """
    def predicate(v):
        return hasattr(v, x)
    return predicate


def not_equal(x):
    """
    Build a predicate that returns True only if value passed to it does not equal x
    """
    def predicate(v):
        return v != x
    return predicate


def equals(x):
    """
    Build a predicate that returns True only if value passed to it equals x
    """
    def predicate(v):
        return v == x
    return predicate


