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
        return (operator(None),)
    elif typeinfo == int and six.PY2:
        return six.integer_types
    else:
        if isinstance(typeinfo, (tuple, list)):
            new_tup = []
            for elem in typeinfo:
                new_tup.extend(_typeinfo_to_tuple_of_types(elem))
            return tuple(new_tup)
        else:
            return (typeinfo,)


def istype(var, type_):
    if type_ is None or type_ == 'self':
        return True

    elif type(type_) == tuple:
        return any(istype(var, subtype) for subtype in type_)

    try:
        if type_ in (Callable, Iterable, Sequence, Mapping):
            raise TypeError()

        if isinstance(var, type_):
            return True

    except TypeError as e:  # must be a typing.* annotation
        if type_ == Callable:
            return hasattr(var, '__call__')
        elif type_ == Iterable:
            return hasattr(var, '__iter__')
        elif type_ == Sequence:
            return hasattr(var, '__iter__') and hasattr(var, '__getattr__') and hasattr(var,
                                                                                        '__len__')
        elif type_ == Mapping:
            return hasattr(var, '__getitem__')

        return type(var) == type_

    return False


def _do_if_not_type(var, type_, fun='default'):
    if type_ in ((type(None),),) and (fun == 'default'):
        return None

    if type_ in (None, (None,), 'self'):
        return var

    if not istype(var, type_):

        if fun == 'default':
            if type_[0] == type(None):
                return None
            else:
                return type_[0](var)

        q = fun()
        if isinstance(q, Exception):
            raise q
        return q
    else:
        return var


