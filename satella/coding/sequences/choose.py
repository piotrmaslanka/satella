from satella.coding.typing import Iteratable, Predicate, T


def choose_one(filter_fun: Predicate[T], iterable: Iteratable) -> T:
    """
    Syntactic sugar for

    >>> choose(filter_fun, iterable, check_multiple=True)

    This exhausts the iterable.

    :param filter_fun: function that returns bool on the single value
    :param iterable: iterable to examine
    :return: single element in the iterable that matches given input
    :raises ValueError: on multiple elements matching, or none at all
    """
    return choose(filter_fun, iterable, True)


def choose(filter_fun: Predicate[T], iterable: Iteratable,
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
        filter_fun, and will raise ValueError if so. If True, this will exhaust the iterator.
        If left at default, False, this may not exhaust the iterator.
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
