import typing as tp

from satella.coding.structures import Proxy
from satella.coding.typing import V

__all__ = ['call_if_nnone', 'iterate_if_nnone', 'Optional']


def iterate_if_nnone(iterable: tp.Optional[tp.Iterable]) -> tp.Iterable:
    """
    Return a generator iterating over every element of iterable if it's not None.

    If it's None, return an empty generator

    :param iterable: iterable to iterate over
    :return: an empty generator if iterable is none, else an iterator over iterable
    """
    if iterable is not None:
        return iter(iterable)
    else:
        return iter(tuple())


def call_if_nnone(clbl: tp.Optional[tp.Callable[..., V]], *args, **kwargs) -> tp.Optional[V]:
    """
    Call clbl with provided arguments, but only if clbl is not None.

    If it's None, then None will be returned. Else, the result of this callable will be returned.

    :param clbl: callable to call, or a None
    :param args: positional arguments to provide to clbl
    :param kwargs: keyword arguments to provide to clbl
    :return: return value or None
    """
    if clbl is not None:
        return clbl(*args, **kwargs)
    else:
        return None


class Optional(Proxy):
    """
    A wrapper for your classes, that does nothing if the object passed in is None.
    It will return an empty Optional in that case.

    Usage example:

    >>> may_be_none = None
    >>> Optional(may_be_none).cancel().result()

    So far operations supported:

    * calling
    * getattr
    * getitem/setitem/delitem
    * testing for truth
    """
    __slots__ = ()

    def __init__(self, obj):
        super().__init__(obj)

    def __getattr__(self, item):
        if getattr(self, '_Proxy__obj') is None:
            return EMPTY_OPTIONAL
        else:
            return super().__getattr__(item)

    def __call__(self, *args, **kwargs):
        if getattr(self, '_Proxy__obj') is None:
            return EMPTY_OPTIONAL
        else:
            return super().__call__(*args, **kwargs)

    def __bool__(self):
        if getattr(self, '_Proxy__obj') is None:
            return False
        else:
            return super().__bool__()

    def __getitem__(self, item):
        if getattr(self, '_Proxy__obj') is None:
            return EMPTY_OPTIONAL
        else:
            return super().__getitem__(item)

    def __setitem__(self, key, value) -> None:
        if getattr(self, '_Proxy__obj') is None:
            return
        return super().__setitem__(key, value)

    def __delitem__(self, key) -> None:
        if getattr(self, '_Proxy__obj') is None:
            return
        return super().__delitem__(key)


EMPTY_OPTIONAL = Optional(None)
