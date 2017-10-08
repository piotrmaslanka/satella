# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import functools
import itertools
import logging
from collections import namedtuple

from .typecheck import typed, coerce, CallSignature

logger = logging.getLogger(__name__)


def _nth(it, n):
    return [x[n] for x in it]


def _adjust(q):
    var, type_ = q
    if type_ in (None, 'self') or isinstance(var, type_):
        return var
    return type_(var)


def typednamedtuple(cls_name, *arg_name_type):
    """
    Returns a new subclass of tuple with named fields.
    Fields will be coerced to type passed in the pair.

    Parameters are tuples of (field name, class/constructor as callable/1)
    """
    fieldnames = _nth(arg_name_type, 0)
    typeops = _nth(arg_name_type, 1)
    MyCls = namedtuple(cls_name, fieldnames)
    mapping = dict(arg_name_type)

    class Wrapper(MyCls):
        __doc__ = MyCls.__doc__
        __name__ = MyCls.__name__

        def __new__(cls, *args, **kwargs):
            nargs = list(map(_adjust, zip(args, typeops[:len(args)]) ))

            for next_field_name in fieldnames[len(nargs):]:
                try:
                    nargs.append(_adjust((kwargs.pop(next_field_name), mapping[next_field_name])))
                except KeyError:
                    raise ValueError('Field %s not given', next_field_name)

            if len(kwargs) > 0:
                raise ValueError('Too many parameters')

            return MyCls.__new__(MyCls, *nargs)

    return Wrapper


