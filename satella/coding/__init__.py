# coding=UTF-8
"""
Just useful objects to make your coding nicer every day
"""
from __future__ import print_function, absolute_import, division

from .typecheck import  typed, List, Tuple, Dict, NewType, Callable, Sequence, \
    TypeVar, Generic, Mapping, Iterable, Union, Any, Optional, CallSignature

from .structures import TimeBasedHeap, CallableGroup
from .monitor import Monitor, RMonitor
