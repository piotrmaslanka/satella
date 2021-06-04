import typing as tp

from satella.coding.structures import Proxy
from satella.coding.typing import V, T

__all__ = ['call_if_nnone', 'iterate_if_nnone', 'Optional', 'extract_optional']


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


class Optional(Proxy[T]):
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
    * comparison (with nonexistent elements always comparing false)
    * membership test (with nonexistent elements always returning false)

    .. warning:: Returned objects via getattr and getitem are NOT wrapped in an
        Optional. You need to do it by hand or just file an issue. I'll add that when I
        need it.

    :param obj: object to wrap
    """

    def __init__(self, obj):
        super().__init__(obj)

    def __contains__(self, item) -> bool:
        me = getattr(self, '_Proxy__obj')
        if me is None:
            return False
        return item in me

    def __eq__(self, other) -> bool:
        me = getattr(self, '_Proxy__obj')
        if me is None:
            return False
        return me == other

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


def extract_optional(v: tp.Union[T, Optional[T]]) -> T:
    """
    If v is an optional, extract the value that it wraps.
    If it is not, return v

    :param v: value to extract the value from
    :return: resulting value
    """
    if isinstance(v, Optional):
        return getattr(v, '_Proxy__obj')
    else:
        return v
