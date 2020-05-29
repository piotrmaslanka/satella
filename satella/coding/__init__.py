"""
Just useful objects to make your coding nicer every day
"""

from .algos import merge_dicts
from .concurrent import Monitor, RMonitor
from .decorators import precondition, for_argument, PreconditionError, short_none, has_keys, \
    attach_arguments, wraps, chain, auto_adapt_to_methods, postcondition
from .fun_static import static_var
from .metaclasses import metaclass_maker, wrap_with, dont_wrap, wrap_property
from .recast_exceptions import rethrow_as, silence_excs, catch_exception, log_exceptions, raises_exception
from .iterators import hint_with_length, SelfClosingGenerator, exhaust
from .deleters import ListDeleter, DictDeleter


__all__ = [
    'hint_with_length', 'SelfClosingGenerator', 'exhaust',
    'Monitor', 'RMonitor', 'merge_dicts',
    'for_argument', 'short_none', 'has_keys',
    'precondition', 'PreconditionError', 'attach_arguments', 'postcondition',
    'rethrow_as', 'silence_excs', 'raises_exception',
    'static_var', 'metaclass_maker',
    'catch_exception', 'wraps', 'wrap_with', 'dont_wrap', 'wrap_property', 'log_exceptions', 'chain',
    'auto_adapt_to_methods',
    'ListDeleter', 'DictDeleter'
]
