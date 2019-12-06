# coding=UTF-8
"""
Just useful objects to make your coding nicer every day
"""
from __future__ import print_function, absolute_import, division

from .algos import merge_dicts
from .concurrent import Monitor, RMonitor, CallableGroup, LockedDataset
from .recast_exceptions import rethrow_as, silence_excs
from .structures import TimeBasedHeap, Heap, typednamedtuple, OmniHashableMixin, Singleton, \
    DictObject
from .decorators import precondition, for_argument
from .fun_static import static_var

__all__ = [
    'typednamedtuple', 'OmniHashableMixin'
                       'TimeBasedHeap', 'Heap', 'CallableGroup', 'DictObject',
    'Monitor', 'RMonitor', 'CallableGroup', 'LockedDataset', 'merge_dicts',
    'for_argument',
    'precondition', 'PreconditionError',
    'rethrow_as', 'silence_excs',
    'Singleton',
    'static_var'
]
