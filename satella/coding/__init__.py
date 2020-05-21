"""
Just useful objects to make your coding nicer every day
"""

from .algos import merge_dicts
from .concurrent import Monitor, RMonitor
from .decorators import precondition, for_argument, PreconditionError, short_none, has_keys, \
    attach_arguments, wraps, chain, auto_adapt_to_methods
from .fun_static import static_var
from .metaclasses import metaclass_maker, wrap_with, dont_wrap, wrap_property
from .recast_exceptions import rethrow_as, silence_excs, catch_exception, log_exceptions
from .iterators import hint_with_length

__all__ = [
    'hint_with_length',
    'Monitor', 'RMonitor', 'merge_dicts',
    'for_argument', 'short_none', 'has_keys',
    'precondition', 'PreconditionError', 'attach_arguments',
    'rethrow_as', 'silence_excs',
    'static_var', 'metaclass_maker',
    'catch_exception', 'wraps', 'wrap_with', 'dont_wrap', 'wrap_property', 'log_exceptions', 'chain',
    'auto_adapt_to_methods'
]
