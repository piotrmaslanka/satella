# coding=UTF-8
"""
Decorator for debug-time typechecking
"""
from __future__ import print_function, absolute_import, division
import six
import logging
import types
import functools

logger = logging.getLogger(__name__)



def typed(*t_args, **t_kwargs):
    """
    Use like:

        @typed(int, six.text_type)
        def display(times, text):
            ...

    int will automatically include long for checking (Python 3 compatibility)
    If you want to check for None, type (None, )
    None for an argument means "do no checking", (None, ) means "type must be NoneType"
    You can pass tuples or lists to match for multiple types

    :param t_args:
    :param t_kwargs:
    :return:
    """

    def typeinfo_to_tuple_of_types(typeinfo):
        if typeinfo is None:
            return (types.NoneType, )
        elif typeinfo == int and six.PY2:
            return six.integer_types
        else:
            if isinstance(typeinfo, (tuple, list)):
                new_tup = []
                for elem in typeinfo:
                    new_tup.extend(typeinfo_to_tuple_of_types(elem))
                return tuple(new_tup)
            else:
                return (typeinfo, )

    t_args = [(typeinfo_to_tuple_of_types(x) if x is not None else None) for x in t_args]

    def outer(fun):

        if not __debug__:
            return fun

        @functools.wraps(fun)
        def inner(*args, **kwargs):

            if isinstance(fun, types.MethodType):   # instancemethod or classmethod
                cargs = args[1:]
            else:
                cargs = args

            for argument, typedescr in zip(cargs, t_args):

                if typedescr is not None:
                    if not isinstance(argument, typedescr):
                        raise TypeError('Got %s, expected %s' % (argument, typedescr))

            return fun(*args, **kwargs)
        return inner

    return outer
