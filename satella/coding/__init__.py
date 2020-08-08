"""
Just useful objects to make your coding nicer every day
"""

from .algos import merge_dicts
from .concurrent import Monitor, RMonitor
from .decorators import precondition, short_none, has_keys, \
    wraps, chain_functions, postcondition, queue_get, auto_adapt_to_methods, \
    attach_arguments, for_argument
from .deleters import ListDeleter, DictDeleter
from .fun_static import static_var
from .iterators import hint_with_length, SelfClosingGenerator, exhaust, chain
from .metaclasses import metaclass_maker, wrap_with, dont_wrap, wrap_property, DocsFromParent, \
    CopyDocsFrom
from .misc import update_if_not_none, update_key_if_none, update_attr_if_none, queue_iterator
from .recast_exceptions import rethrow_as, silence_excs, catch_exception, log_exceptions, \
    raises_exception

__all__ = [
    'update_if_not_none', 'DocsFromParent', 'update_key_if_none', 'queue_iterator',
    'update_attr_if_none',
    'hint_with_length', 'SelfClosingGenerator', 'exhaust', 'chain',
    'Monitor', 'RMonitor', 'merge_dicts',
    'short_none', 'has_keys', 'CopyDocsFrom',
    'precondition', 'postcondition', 'queue_get',
    'rethrow_as', 'silence_excs', 'raises_exception',
    'static_var', 'metaclass_maker',
    'catch_exception', 'wraps', 'wrap_with', 'dont_wrap', 'wrap_property', 'log_exceptions',
    'chain_functions',
    'ListDeleter', 'DictDeleter', 'for_argument', 'attach_arguments', 'auto_adapt_to_methods',
]
