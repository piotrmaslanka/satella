import typing as tp

T = tp.TypeVar('T')

__all__ = ['choose', 'choose_one']


def choose_one(filter_fun: tp.Callable[[T], bool], iterable: tp.Iterable[T]) -> T:
    """
    Syntactic sugar for

    >>> choose(filter_fun, iterable, True)

    :param filter_fun: function that returns bool on the single value
    :param iterable: iterable to examine
    :return: single element in the iterable that matches given input
    :raises ValueError: on multiple elements matching, or none at all
    """
    return choose(filter_fun, iterable, True)


def choose(filter_fun: tp.Callable[[T], bool], iterable: tp.Iterable[T],
           check_multiple: bool = False) -> T:
    """
    Return a single value that exists in given iterable.

    Essentially the same as:

    >>> next(iter(filter(filter_fun, iterable)))

    but raises a different exception if nothing matches (and if there are multiple matches
    and check_multiple is True).
    If check_multiple is True this guarantees to exhaust the generator (if passed).

    :param filter_fun: function that returns bool on the single value
    :param iterable: iterable to examine
    :param check_multiple: if True, this will check if there are multiple entries matching
        filter_fun, and will raise ValueError if so
    :return: single element in the iterable that matches given input
    :raises ValueError: on multiple elements matching (if check_multiple), or none at all
    """
    elem_candidate = None
    found = False
    for elem in iterable:
        if filter_fun(elem):
            if not check_multiple:
                return elem

            if found:
                raise ValueError(
                    'Multiple values (%s, %s) seen' % (repr(elem_candidate), repr(elem)))
            elem_candidate = elem
            found = True

    if not found:
        raise ValueError('No elements matching given filter seen')

    return elem_candidate
