import logging
import typing as tp

logger = logging.getLogger(__name__)

__all__ = ['is_last']
T = tp.TypeVar('T')


def is_last(lst: tp.List[T]) -> tp.Generator[tp.Tuple[bool, T], None, None]:
    """
    Return every element of the list, alongside a flag telling is this the last element.

    Use like:

    >>> for is_last, element in is_last(my_list):
    >>> if is_last:
    >>>     ...

    :param lst: list to iterate thru
    :return: a generator returning (bool, T)
    """
    for i, elem in enumerate(lst):
        if i == len(lst) - 1:
            yield True, elem
        else:
            yield False, elem
