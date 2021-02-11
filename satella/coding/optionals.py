import typing as tp

from satella.coding.typing import V

__all__ = ['call_if_nnone', 'iterate_if_nnone']


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
