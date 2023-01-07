"""
Just useful objects to make your coding nicer every day
"""

from .ctxt_managers import EmptyContextManager
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
from .misc import update_if_not_none, update_key_if_none, update_attr_if_none, queue_iterator, \
    update_key_if_not_none, source_to_function, update_key_if_true, \
    get_arguments, call_with_arguments, chain_callables, Closeable, contains, \
    enum_value, length
from .environment import Context
from .overloading import overload, class_or_instancemethod, TypeSignature
from .recast_exceptions import rethrow_as, silence_excs, catch_exception, log_exceptions, \
    raises_exception, reraise_as
from .expect_exception import expect_exception
from .deep_compare import assert_equal, InequalityReason, Inequal

__all__ = [
    'EmptyContextManager', 'Context', 'length',
    'assert_equal', 'InequalityReason', 'Inequal',
    'Closeable', 'contains', 'enum_value',
    'expect_exception',
    'overload', 'class_or_instancemethod', 'TypeSignature',
    'update_if_not_none', 'DocsFromParent', 'update_key_if_none', 'queue_iterator',
    'update_attr_if_none', 'update_key_if_not_none', 'source_to_function',
    'update_key_if_true',
    'hint_with_length', 'SelfClosingGenerator', 'exhaust', 'chain',
    'Monitor', 'RMonitor', 'merge_dicts', 'chain_callables',
    'short_none', 'has_keys', 'CopyDocsFrom',
    'precondition', 'postcondition', 'queue_get',
    'rethrow_as', 'silence_excs', 'raises_exception',
    'static_var', 'metaclass_maker',
    'catch_exception', 'wraps', 'wrap_with', 'dont_wrap', 'wrap_property', 'log_exceptions',
    'chain_functions', 'get_arguments', 'call_with_arguments',
    'ListDeleter', 'DictDeleter', 'for_argument', 'attach_arguments', 'auto_adapt_to_methods',
]
