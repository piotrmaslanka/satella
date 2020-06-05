import typing as tp

T = tp.TypeVar('T')

__all__ = ['choose']


def choose(filter_fun: tp.Callable[[T], bool], iterable: tp.Iterable[T],
           dont_check_multiple: bool = False) -> T:
    """
    Return a single value that exists in given iterable.

    Essentially the same as:

    >>> next(iter(filter(filter_fun, iterable)))

    but raises a different exception if nothing matches (and if there are multiple matches).
    This will also look through the entire list

    :param filter_fun: function that returns bool on the single value
    :param iterable: iterable to examine
    :param dont_check_multiple: if True, this won't check if there are multiple entries matching
        filter_fun, but will bail on first found element
    :return: single element in the iterable that matches given input
    :raises ValueError: on multiple elements matching, or none at all
    """
    elem_candidate = None
    found = False
    for elem in iterable:
        if filter_fun(elem):
            if dont_check_multiple:
                return elem

            if found:
                raise ValueError(
                    'Multiple values (%s, %s) seen' % (repr(elem_candidate), repr(elem)))
            elem_candidate = elem
            found = True

    if not found:
        raise ValueError('No elements matching given filter seen')

    return elem_candidate
