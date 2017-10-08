# coding=UTF-8
"""
Just useful objects to make your coding nicer every day
"""
from __future__ import print_function, absolute_import, division

from .algos import merge_dicts
from .monitor import Monitor, RMonitor
from .structures import TimeBasedHeap, CallableGroup, Heap
from .typecheck import typed, List, Tuple, Dict, NewType, Callable, Sequence, \
    TypeVar, Generic, Mapping, Iterable, Union, Any, Optional, CallSignature, Number
from .recast_exceptions import rethrow_as, silence_excs

__all__ = [
    'TimeBasedHeap', 'Heap', 'CallableGroup',
    'Monitor', 'RMonitor', 'merge_dicts',
    'typed', 'List', 'Tuple', 'Dict', 'NewType', 'Callable', 'Sequence',
    'TypeVar', 'Generic', 'Mapping', 'Iterable', 'Union', 'Any', 'Optional', 'CallSignature', 'Number',
    'rethrow_as', 'silence_excs'
]

