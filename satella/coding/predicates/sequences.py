import typing as tp


def length_less_than(x) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is less than x

    :param x: value of x
    """
    def predicate(v):
        return len(v) < x
    return predicate


def length_is(x) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is x
    """
    def predicate(v):
        return len(v) == x
    return predicate


def length_multiple_of(x) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is a multiple of x
    """
    def predicate(v):
        return not (len(v) % x)
    return predicate
