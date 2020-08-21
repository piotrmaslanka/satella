import typing as tp
import math

Number = tp.Union[float, int]
Predicate = tp.Callable[[Number], bool]


def between(left: Number = -math.inf, right: Number = math.inf,
            incl_left: bool = True, incl_right: bool = True) -> Predicate:
    """
    Build a predicate to check whether a given number is in particular range

    :param left: predicate will be true for numbers larger than this
    :param right: predicate will be true for numbers smaller than this
    :param incl_left: whether to include left in the range for the predicate. Set to True
        will result in a <= operator, whereas False will result in a >
    :param incl_right: whether to include left in the range for the predicate
    :param attribute: if given, then it will first try to access given attribute of v
    """
    def predicate(x: Number) -> bool:
        if incl_left:
            if x < left:
                return False
        else:
            if x <= left:
                return False

        if incl_right:
            if x > right:
                return False
        else:
            if x >= right:
                return False

        return True
    return predicate
