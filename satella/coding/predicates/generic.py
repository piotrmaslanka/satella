import typing as tp
from .shared import get_attribute


def one_of(*args, attribute: tp.Optional[str] = None) -> tp.Callable[[tp.Any], bool]:
    """
    Return a predicate that will return True if passed value equals to one of the arguments

    :param args: a list of arguments on which the predicate will return True
    :param attribute: if given, then it will first try to access given attribute of v
    """
    def predicate(v):
        return get_attribute(v, attribute) in args
    return predicate


