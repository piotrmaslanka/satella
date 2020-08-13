import collections
import random
import typing as tp

from .merger import merge_series

__all__ = ['stringify', 'split_shuffle_and_join', 'one_tuple',
           'merge_series']


def _stringify_none(str_none, stringifier):
    if str_none:
        return stringifier(None)
    return None


T = tp.TypeVar('T')


def one_tuple(x: tp.Iterable[T]) -> tp.Iterator[tp.Tuple[T]]:
    """
    Change a sequence of iterables into a sequence that displays each element as
    a part of one-element tuple. Essentially syntactic sugar for:

    >>> for y in x:
    >>>     yield y,

    :param x: sequence to tupleify
    :return: a iterator of one-element tuples
    """
    for y in x:
        yield y,


def split_shuffle_and_join(entries: tp.List[T],
                           whether_to_shuffle: tp.Callable[[T], bool] = lambda x: True,
                           not_shuffled_to_front: bool = True) -> tp.List[T]:
    """
    Split elements in entries into two groups - one group, called True, is the one for which
    whether_to_shuffle(elem) is True, the other is False.

    Shuffle the group True.

    If not_shuffled_to_front, elements in the group False will go at the beginning of the returned
    list, after which will go elements shuffled. If it's False, the not-shuffled elements will be
    at the back of the list.

    Order of the not shuffled elements will be preserved.

    :param entries: list of elements
    :param whether_to_shuffle: a decider to which group does given element belong?
    :param not_shuffled_to_front: if True then not shuffled elements will be put before shuffled,
        else the not shuffled elements will be at the back of the list
    :return: list altered to specification
    """

    not_shuffled, shuffled = [], []
    for elem in entries:
        (shuffled if whether_to_shuffle(elem) else not_shuffled).append(elem)

    random.shuffle(shuffled)

    if not_shuffled_to_front:
        return not_shuffled + shuffled
    else:
        return shuffled + not_shuffled


def stringify(obj: tp.Union[tp.Any], stringifier: tp.Callable[[tp.Any], str] = str,
              recursively: bool = False,
              str_none: bool = False) -> tp.Dict[str, str]:
    """
    Stringify all object:

    ie. if a dict, put every item and key (if a dict is given) through stringify.
        if a list, put every item through stringify
        else just call stringify on it.

        Note that if you use recursively, then dicts and lists are allowed to be valid elements of the returned
        representation!

    :param obj: a list or a dict
    :param stringifier: function that accepts any arguments and returns a string representation
    :param recursively: whether to recursively stringify elements, ie. stringify will be called on all the children
    :param str_none: whether to return None if given a None. If True, "None" will be returned instead
    :return: stringified object
    """
    if isinstance(obj, collections.abc.Mapping):
        make_str = (lambda obj2: stringify(obj2, stringifier, True, str_none)) if recursively else \
            stringifier
        return {make_str(k): make_str(v) for k, v in obj.items()}
    elif isinstance(obj, collections.abc.Sequence):
        make_str = (lambda obj2: stringify(obj2, stringifier, True, str_none)) if recursively else \
            stringifier
        return [make_str(v) for v in obj]
    elif obj is None:
        return _stringify_none(str_none, stringifier)
    else:
        return stringifier(obj)
