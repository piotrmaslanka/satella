import typing as tp


def one_of(*args) -> tp.Callable[[tp.Any], bool]:
    """
    Return a predicate that will return True if passed value equals to one of the arguments

    :param args: a list of arguments on which the predicate will return True
    """
    def predicate(v):
        return v in args
    return predicate


def length_multiple_of(x) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is a multiple of x
    """
    def predicate(v):
        return not (len(v) % x)
    return predicate


def length_is(x) -> tp.Callable[[tp.Sequence], bool]:
    """
    Return a predicate that will return True if length of sequence is x
    """
    def predicate(v):
        return len(v) == x
    return predicate
