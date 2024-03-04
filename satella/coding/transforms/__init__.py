import collections
import enum
import random
import typing as tp

from satella.coding.decorators import for_argument
from .base64 import b64encode
from .interpol import linear_interpolate
from .jsonify import jsonify
from .merge_list import merge_list
from .merger import merge_series
from .percentile import percentile
from .predicates import is_subset
from .words import hashables_to_int

__all__ = ['stringify', 'split_shuffle_and_join', 'one_tuple', 'none_if_false',
           'merge_series', 'pad_to_multiple_of_length', 'clip', 'hashables_to_int',
           'jsonify', 'intify', 'percentile', 'b64encode', 'linear_interpolate',
           'merge_list', 'is_subset', 'unpack_dict']

from satella.coding.typing import T, NoArgCallable, Appendable, Number, Predicate, K, V


def unpack_dict(dct: tp.Dict[K, V], *args: K,
                map_through: tp.Callable[[V], V] = lambda y: y,
                raise_if_not_found: bool = True) -> tp.Iterator[V]:
    """
    Unpack a dictionary by accessing it's given keys in parallel.

    Example:

    >>> a, b, c = unpack_dict({1:2, 2:3, 4:5}, 1, 2, 4)
    >>> assert a == 2 and b == 3 and c == 5

    :param dct: dictionary to unpack
    :param args: keys in this dictionary
    :param map_through: a keyword argument, callable that will be called with
        each value returned and the result of this callable will be returned
    :param raise_if_not_found: a KeyError will be returned upon encountering a key
        that does not exist. If set to False, a None will be returned.
    :return: an iterator
    :raises KeyError: a key was not found
    """
    for key in args:
        try:
            yield map_through(dct[key])
        except KeyError:
            if not raise_if_not_found:
                yield None
            else:
                raise


def none_if_false(y: tp.Any) -> tp.Optional[tp.Any]:
    """
    Return None if y is false, else return y

    :param y: value to check
    :return: None if y is false, else y
    """
    if not y:
        return None
    return y


def clip(v: Number, minimum: Number, maximum: Number) -> Number:
    """
    Clip v so it conforms to minimum <= v <= maximum

    :param v: value to clip
    :param minimum: minimum
    :param maximum: maximum
    :return: clipped value
    """
    if v < minimum:
        return minimum
    if v > maximum:
        return maximum
    return v


@for_argument(list)
def pad_to_multiple_of_length(seq: Appendable[T], multiple_of: int,
                              pad_with: tp.Optional[T] = None,
                              pad_with_factory: tp.Optional[NoArgCallable[T]] = None) -> \
        Appendable[T]:
    """
    Make sequence multiple of length, ie. append elements to the sequence
    until it's length is a multiple of multiple_of.

    :param seq: sequence to lengthify
    :param multiple_of: sequence returned will be a multiple of this length.
    :param pad_with: argument with which to pad the sequence
    :param pad_with_factory: a callable/0 that returns an element with which to pad the sequence
    :return: a list with elements
    """
    if pad_with is not None and pad_with_factory is not None:
        raise ValueError('You need to give either pad_with or pad_with_factory')

    if pad_with_factory is None:
        def pad_with_factory():
            return pad_with

    while len(seq) % multiple_of:
        seq.append(pad_with_factory())
    return seq


def _stringify_none(str_none: tp.Optional[str],
                    stringifier: tp.Callable[[tp.Any], str]) -> tp.Optional[str]:
    if str_none:
        return stringifier(None)
    return None


def one_tuple(x: tp.Iterable[T]) -> tp.Iterator[tp.Tuple[T]]:
    """
    Change a sequence of iterables into a sequence that displays each element as
    a part of one-element tuple. Essentially syntactic sugar for:

    >>> for z in x:
    >>>     yield z,

    :param x: sequence to tupleify
    :return: a iterator of one-element tuples
    """
    for z in x:
        yield z,


def intify(v: tp.Any) -> int:
    """
    Attempt to convert v to an int.

    None will be converted to 0.

    Any object will have int() called on it.

    Failing that, it's length will be taken.

    Failing that, ValueError will be raised

    :param v: parameter
    :return: int representation
    """
    if v is None:
        return 0

    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return len(v)
        except (AttributeError, TypeError, ValueError):
            raise ValueError('Unable to convert %s to int' % (v,))


def split_shuffle_and_join(entries: tp.List[T],
                           whether_to_shuffle: Predicate[T] = lambda x: True,
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
              str_none: bool = False) -> tp.Union[tp.List[str], tp.Dict[str, str], str]:
    """
    Stringify all object:

    ie. if a dict, put every item and key (if a dict is given) through stringify.
        if a list, put every item through stringify
        else just call stringify on it.

    Note that if you use recursively, then dicts and lists are allowed to be valid elements of the
    returned representation!

    Note that enums will be converted to their labels. eg:

    >>> class Enum(enum.Enum):
    >>>     A = 0
    >>> assert stringify(Enum.A) == 'A'

    :param obj: a list or a dict
    :param stringifier: function that accepts any arguments and returns a string representation
    :param recursively: whether to recursively stringify elements, ie. stringify will be called on
        all the children
    :param str_none: whether to return None if given a None. If True, "None" will be returned
        instead
    :return: stringified object
    """
    if isinstance(obj, str):
        y = obj
    elif isinstance(obj, enum.Enum):
        y = obj.name
    elif isinstance(obj, collections.abc.Mapping):
        make_str = (lambda obj2: stringify(obj2, stringifier, True, str_none)) if recursively else \
            stringifier
        y = {make_str(k): make_str(v) for k, v in obj.items()}
    elif isinstance(obj, collections.abc.Sequence):
        make_str = (lambda obj2: stringify(obj2, stringifier, True, str_none)) if recursively else \
            stringifier
        y = [make_str(v) for v in obj]
    elif obj is None:
        y = _stringify_none(str_none, stringifier)
    else:
        y = stringifier(obj)
    return y
