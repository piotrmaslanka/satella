# coding=UTF-8
from __future__ import print_function, absolute_import, division

import numbers
import typing

__all__ = [
    'Callable', 'Sequence', 'Number', 'Mapping', 'Iterable', 'Any',
    'Optional', 'TypeVar', 'List', 'Tuple', 'Dict', 'Set',
    '_NotGiven', '_NoDefault', '_NOP', '_TRUE'
]

Callable = lambda *args: typing.Callable
Sequence = typing.Sequence
Number = numbers.Real
Mapping = typing.Mapping
Iterable = typing.Iterable
Any = typing.Any
Optional = lambda opt: opt + (None,) if isinstance(opt, tuple) else (opt, None)
TypeVar = typing.TypeVar
List = lambda *opt: list
Tuple = lambda *opt: tuple
Dict = lambda *p: dict
Set = lambda *p: set


# Internal tokens - only instances will be
class _NotGiven(object):
    pass


class _NoDefault(object):
    pass


_NOP = lambda x: x
_TRUE = lambda x: True
