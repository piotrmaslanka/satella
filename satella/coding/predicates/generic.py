import typing as tp


def one_of(*args) -> tp.Callable[[tp.Any], bool]:
    """
    Return a predicate that will return True if passed value equals to one of the arguments

    :param args: a list of arguments on which the predicate will return True
    """
    def predicate(v):
        return v in args
    return predicate
