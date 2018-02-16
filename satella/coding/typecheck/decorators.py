# coding=UTF-8
from __future__ import print_function, absolute_import, division
import functools
import warnings
import six

from .corechk import *
from .basics import *

__all__ = [
    'typed',
    'coerce',
    'checked_coerce',
    'for_argument',
    'PreconditionError', 'precondition'
]

def typed(*t_args, **t_kwargs):
    """
    Use like:

        @typed(int, six.text_type)
        def display(times, text):
            ...

    You can also check for return type with kw argument of "returns", ie.

        @typed(int, int, returns=int)
        def sum(a, b):
            return a+b

    Or
        @typed('self', a, b):
        def method(self, a, b):
        ..

    If you specify extra argument - mandatory=True - type will always be
    checked, regardless if debug mode is enabled

    Same rules apply.

    int will automatically include long for checking (Python 3 compatibility)
    If you want to check for None, type (None, )
    None for an argument means "do no checking", (None, ) means "type must be
    NoneType". You can pass tuples or lists to match for multiple types

    :param t_args:
    :param t_kwargs:
    """

    t_args = [(_typeinfo_to_tuple_of_types(x) if x is not None else None)
              for x in t_args]

    t_retarg = t_kwargs.get('returns', None)
    is_mandatory = t_kwargs.get('mandatory', False)

    if t_retarg is not None:
        t_retarg = _typeinfo_to_tuple_of_types(t_retarg)

    def outer(fun):
        if (not __debug__) and (not is_mandatory):
            return fun

        @functools.wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method
            for argument, typedescr in zip(args, t_args):
                if not istype(argument, typedescr):
                    raise TypeError('Got %s, expected %s' % (
                        type(argument), typedescr))

            rt = fun(*args, **kwargs)

            if not istype(rt, t_retarg):
                raise TypeError('Returned %s, expected %s' % (
                    type(rt), t_retarg))

            return rt

        return inner

    return outer


def coerce(*t_args, **t_kwargs):
    """#todo banana banana banana"""
    warnings.warn('Using coerce is considered harmful', DeprecationWarning)

    t_args = [(_typeinfo_to_tuple_of_types(x, operator=_NOP))
              for x in t_args]

    def argify(args):
        return [_do_if_not_type(argument, typedescr) \
                for argument, typedescr in six.moves.zip_longest(args, t_args)]

    t_retarg = t_kwargs.get('returns', None)

    t_retarg = _typeinfo_to_tuple_of_types(t_retarg, operator=_NOP)

    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method

            new_args = argify(args)

            rt = fun(*new_args, **kwargs)
            return _do_if_not_type(rt, t_retarg)

        return inner

    return outer


def checked_coerce(*t_args, **t_kwargs):
    """#todo banana banana banana"""
    warnings.warn('Using checked_coerce is considered harmful', DeprecationWarning)

    def ptc(item, pt=list):
        if item is None:
            return None, None
        elif isinstance(item, pt):
            if len(item) == 2:
                return item[0], item[1]
        return item, None

    def sselector(q, z, operator=None, pt=list):
        s = ptc(q, pt=pt)[z]
        if s is None and operator is None:
            return None
        return _typeinfo_to_tuple_of_types(s, operator=operator)

    t_args_t = [sselector(x, 0) for x in t_args]
    t_args_c = [sselector(x, 1, operator=_NOP) for x in t_args]

    def argify(args):
        return [_do_if_not_type(argument, typedescr) \
                for argument, typedescr in six.moves.zip_longest(args, t_args_c)]

    t_retarg = t_kwargs.get('returns', None)
    t_retarg_t = sselector(t_retarg, 0, pt=tuple)
    t_retarg_c = sselector(t_retarg, 1, operator=_NOP, pt=tuple)

    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method

            for argument, typedescr in zip(args, t_args_t):
                if not istype(argument, typedescr):
                    raise TypeError('Got %s, expected %s' % (
                        type(argument), typedescr))

            rt = fun(*argify(args), **kwargs)
            if not istype(rt, t_retarg_t):
                raise TypeError('Returned %s, expected %s' % (
                    type(rt), t_retarg_t))

            return _do_if_not_type(rt, t_retarg_c)

        return inner

    return outer


class PreconditionError(ValueError):
    """
    A precondition was not met for the argument
    """


def precondition(*t_ops):
    """
    Check that a precondition happens for given parameter.
    Only positional arguments are supported.

    You can do it like this:

    @precondition(lambda x: x == 1)
    def return_two(x):
        return x*2

    or

    @precondition('x == 1')
    def return_two(x):
        ..

    If None is passed then argument will be always assumed to be True.
    You can use all standard locals in precondition.

    You function call will return a PreconditionError (subclass of
    ValueError) if a precondition fails
    """

    tn_ops = []

    for t_op in t_ops:
        if t_op is None:
            precond = _TRUE
        elif isinstance(t_op, six.string_types):
            q = dict(globals())
            exec('_precond = lambda x: ' + t_op, q)
            precond = q['_precond']
        else:
            precond = t_op

        tn_ops.append(precond)

    from satella.coding.recast_exceptions import rethrow_as

    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            assert len(args) >= len(tn_ops), 'More preconditions than positional arguments!'
            with rethrow_as(TypeError, PreconditionError):
                for arg, precond in six.moves.zip_longest(args, tn_ops, fillvalue=_TRUE):
                    print(arg, precond, precond.__doc__)
                    if not precond(arg):
                        raise PreconditionError(
                            'Argument of value %s failed precondition check' % (arg,))
            return fun(*args, **kwargs)

        return inner

    return outer


def for_argument(*t_ops, **t_kwops):
    t_ops = [_NOP if op == 'self' else op for op in t_ops]

    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method
            assert len(args) >= len(t_ops)
            return fun(*((_NOP if op is None else op)(arg) for arg, op in
                         six.moves.zip_longest(args, t_ops)),
                       **{k: t_kwops.get(k, _NOP)(v) for k, v in kwargs.items()})

        return inner

    return outer
