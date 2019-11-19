# coding=UTF-8
from __future__ import print_function, absolute_import, division

import six

__all__ = [
    '_typeinfo_to_tuple_of_types', 'istype', '_do_if_not_type'
]

from .basics import *


def _typeinfo_to_tuple_of_types(typeinfo, operator=type):
    if typeinfo == 'self':
        return None
    elif typeinfo is None:
        return operator(None),
    elif typeinfo == int and six.PY2:
        return six.integer_types
    else:
        if isinstance(typeinfo, (tuple, list)):
            new_tup = []
            for elem in typeinfo:
                new_tup.extend(_typeinfo_to_tuple_of_types(elem))
            return tuple(new_tup)
        else:
            return typeinfo,


def istype(var, type_):
    ret_v = False

    if type_ is None or type_ == 'self':
        ret_v = True

    elif type(type_) == tuple:
        ret_v = any(istype(var, subtype) for subtype in type_)

    elif type_ in (Callable, Iterable, Sequence, Mapping):
        if type_ == Callable:
            ret_v = hasattr(var, '__call__')
        elif type_ == Iterable:
            ret_v = hasattr(var, '__iter__')
        elif type_ == Sequence:
            ret_v = hasattr(var, '__iter__') and hasattr(var, '__getattr__') and hasattr(var,
                                                                                        '__len__')
        elif type_ == Mapping:
            ret_v = hasattr(var, '__getitem__')
    else:
        try:
            if isinstance(var, type_):
                ret_v = True
        except TypeError:  # must be a typing.* annotation
            ret_v = type(var) == type_

    return ret_v


def _do_if_not_type(var, type_, fun='default'):
    if type_ in ((type(None),),) and (fun == 'default'):
        ret_v = None

    elif type_ in (None, (None,), 'self'):
        ret_v = var

    elif not istype(var, type_):

        if fun == 'default':
            ret_v = None if type_[0] == type(None) else type_[0](var)
        else:
            q = fun()
            if isinstance(q, Exception):
                raise q
            ret_v = q
    else:
        ret_v = var

    return ret_v
