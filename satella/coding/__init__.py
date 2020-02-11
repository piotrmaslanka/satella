"""
Just useful objects to make your coding nicer every day
"""

from .algos import merge_dicts
from .concurrent import Monitor, RMonitor
from .decorators import precondition, for_argument, PreconditionError, short_none, has_keys
from .fun_static import static_var
from .metaclasses import metaclass_maker
from .recast_exceptions import rethrow_as, silence_excs, catch_exception

__all__ = [
    'Monitor', 'RMonitor', 'merge_dicts',
    'for_argument', 'short_none', 'has_keys',
    'precondition', 'PreconditionError',
    'rethrow_as', 'silence_excs',
    'static_var', 'metaclass_maker',
    'catch_exception',
]
