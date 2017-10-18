# coding=UTF-8
"""
Just useful objects to make your coding nicer every day
"""
from __future__ import print_function, absolute_import, division

from .concurrent import Monitor, RMonitor, CallableGroup
from .algos import merge_dicts
from .recast_exceptions import rethrow_as, silence_excs
from .typecheck import typed, Callable, Sequence, \
    TypeVar, Mapping, Iterable, Any, Optional, CallSignature, \
    Number, coerce, Set, Dict, List, Tuple, checked_coerce, for_argument, \
    precondition, PreconditionError
from .structures import TimeBasedHeap, Heap, typednamedtuple, OmniHashableMixin

__all__ = [
    'typednamedtuple', 'OmniHashableMixin'
    'TimeBasedHeap', 'Heap', 'CallableGroup',
    'Monitor', 'RMonitor', 'merge_dicts',
    'typed', 'NewType', 'Callable', 'Sequence', 'coerce'
    'TypeVar','Mapping', 'Iterable', 'Union', 'Any', 'Optional',
    'CallSignature', 'Number',
    'Set', 'Dict', 'List', 'Tuple', 'checked_coerce', 'for_argument',
    'precondition', 'PreconditionError',
    'rethrow_as', 'silence_excs'
]

