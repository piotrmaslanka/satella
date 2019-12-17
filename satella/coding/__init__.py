"""
Just useful objects to make your coding nicer every day
"""

from .algos import merge_dicts
from .concurrent import Monitor, RMonitor, CallableGroup, LockedDataset
from .recast_exceptions import rethrow_as, silence_excs
from .structures import TimeBasedHeap, Heap, typednamedtuple, OmniHashableMixin, Singleton, \
    DictObject, apply_dict_object
from .decorators import precondition, for_argument, PreconditionError
from .fun_static import static_var


__all__ = [
    'typednamedtuple', 'OmniHashableMixin'
                       'TimeBasedHeap', 'Heap', 'CallableGroup', 'DictObject', 'apply_dict_object',
    'Monitor', 'RMonitor', 'CallableGroup', 'LockedDataset', 'merge_dicts',
    'for_argument',
    'precondition', 'PreconditionError',
    'rethrow_as', 'silence_excs',
    'Singleton',
    'static_var'
]
