import logging
import typing as tp

logger = logging.getLogger(__name__)

__all__ = ['is_last']
T = tp.TypeVar('T')


# shamelessly copied from https://medium.com/better-programming/is-this-the-last-element-of-my-python-for-loop-784f5ff90bb5
def is_last(lst: tp.Iterable[T]) -> tp.Generator[tp.Tuple[bool, T], None, None]:
    """
    Return every element of the list, alongside a flag telling is this the last element.

    Use like:

    >>> for is_last, element in is_last(my_list):
    >>> if is_last:
    >>>     ...

    :param lst: list to iterate thru
    :return: a generator returning (bool, T)
    """
    iterable = iter(lst)
    ret_var = next(iterable)
    for val in iterable:
        yield False, ret_var
        ret_var = val
    yield True, ret_var


def add_next(lst: tp.Iterable[T]) -> tp.Generator[tp.Tuple[T, tp.Optional[T]], None, None]:
    """
    Yields a 2-tuple of given iterable, presenting the next element as second element of the tuple.

    The last element will be the last element alongside with a None

    Example:

    >>> list(add_next([1, 2, 3, 4, 5])) == [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)]
    """
    iterator = iter(lst)
    prev_val = next(iterator)
    for val in iterator:
        yield prev_val, val
        prev_val = val
    yield prev_val, None

