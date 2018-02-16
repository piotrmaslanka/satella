# coding=UTF-8
from __future__ import print_function, absolute_import, division
"""
Decorator for debug-time typechecking

If you are simultaneously using @typed and @coerce, use them in following order:

    @coerce(...)
    @typed(...)
    def fun(..):
        ...

"""

import inspect
import logging
from ..coding.recast_exceptions import silence_excs
import six
from copy import copy
import typing
from collections import namedtuple
import functools
import numbers
import itertools
import warnings


logger = logging.getLogger(__name__)


Callable = lambda *args: typing.Callable
Sequence = typing.Sequence
Number = numbers.Real
Mapping = typing.Mapping
Iterable = typing.Iterable
Any = typing.Any
Optional = lambda opt: opt + (None, ) if isinstance(opt, tuple) else (opt, None)
TypeVar = typing.TypeVar
List = lambda *opt: list
Tuple = lambda *opt: tuple
Dict = lambda *p: dict
Set = lambda *p: set

# Internal tokens - only instances will be
class _NotGiven(object):
    pass


class _NoDefault(object):
    pass


__NOP = lambda x: x
__TRUE = lambda x: True
_CSArgument = namedtuple('_CSArgument', ('name', 'required', 'default_value'))


class CSArgument(_CSArgument):
    def __str__(self):
        p = ['Argument ' + self.name]
        if not self.required:
            p.append('optional with default %s' % (self.default_value,))
        return ' '.join(p)

    def __eq__(self, other):
        """
        Is other argument same as this, in name/default value if present?
        :param other: CSArgument
        :return: bool
        """
        return self.name == other.name and \
               self.required == other.required and \
               self.default_value == other.default_value


class CSVarargsPlaceholder(CSArgument):
    pass


class CSKwargsPlaceholder(CSArgument):
    pass


class TypeErrorReason(object):
    pass


class CSTypeError(TypeError):
    """
    A TypeError exception on steroids
    """

    def __str__(self):
        return 'Problem with argument %s' % (arg.name,)

    def __init__(self, arg):
        """
        :param arg: Argument definition
        :type arg: CSArgument
        """
        super(CSTypeError, self).__init__(str(self))
        self.arg = arg


class CSBadTypeError(CSTypeError):
    def __init__(self, arg, expected, got):
        super(CSBadTypeError, self).__init__(arg)

        self.expected = expected
        self.got = got

    def __str__(self):
        return 'Bad type given for arg %s, expected %s got %s' % (
            self.arg.name, self.expected, self.got)


class CSNotGivenError(CSTypeError):
    def __str__(self):
        return 'Value for argument %s not given' % (self.arg.name,)


class CSMultipleValuesGivenError(CSTypeError):
    def __str__(self):
        return 'Got multiple values for argument' % (self.arg.name,)


class CallSignature(object):
    """
    Call signature of a callable.
    
    Properties:
      - has_varargs (Bool) - if has varargs
      - has_kwargs (Bool) - if has kwargs
      - locals (Dict[str => CSArgument]) - list of locals this function call
        will generate
      - pos_args (List[CSArgument)] - list of positional arguments
      - varargs_name ((str, None)) - name of varargs argument, or None if
        not present
      - kwargs_name ((str, None)) - name of kwargs argument, or None if
        not present
    """

    def count_required_positionals(self):
        c = 0
        for a in self.pos_args:
            if a.required:
                c += 1
        return c

    def __eq__(self, other):
        """
        Compare if two call signatures are IDENTICAL
        :param other: CallSignature
        :return: bool
        """

        if any(a != b for a, b in zip(self.pos_args, other.pos_args)):
            return False

        return self.has_kwargs == other.has_kwargs and \
               self.has_varargs == other.has_varargs

    def __init__(self, callable):
        args, varargs, kwargs, defaults = inspect.getargspec(callable)

        defaults = defaults or ()
        # pad them
        while len(defaults) < len(args):
            defaults = [_NoDefault] + list(defaults)

        # process positionals
        self.pos_args = []
        self.locals = {}
        for arg, default in zip(args, defaults):
            cs_arg = CSArgument(arg,
                                default is _NoDefault,
                                default)
            self.pos_args.append(cs_arg)
            self.locals[arg] = cs_arg

        self.varargs_name = varargs
        if varargs is not None:
            self.has_varargs = True
            self.locals[self.varargs_name] = CSVarargsPlaceholder(
                self.varargs_name, False, [])
        else:
            self.has_varargs = False

        self.kwargs_name = kwargs
        if kwargs is not None:
            self.has_kwargs = True
            self.locals[self.kwargs_name] = CSKwargsPlaceholder(
                self.kwargs_name, False, {})
        else:
            self.has_kwargs = False

    def to_invocation(self, locals):
        """
        Return an invocation to the function reconstructed from its locals
        :param locals: as returned by .result()
        :return: tuple of (args, kwargs)
        """
        locals = copy(locals)
        args = []

        for arg in self.pos_args:
            if arg.name in locals:
                args.append(locals.pop(arg.name))
            elif not arg.required:
                args.append(arg.default_value)
                del locals[arg.name]

        return args, locals

    def result(self, *args, **kwargs):
        """
        Simulate a function call, see what locals are defined
        
        Return a dict of (local_variable_name => it's value),
        or TypeError

        :param args: function call parameters
        :param kwargs: function call parameters
        :return: dict
        :raise CSTypeError: call would raise a TypeError
        """
        assert len(args) >= self.count_required_positionals()

        locals = {}

        # positional
        for arg, value in itertools.izip_longest(self.pos_args,
                                                 args[:len(self.pos_args)],
                                                 fillvalue=_NotGiven):

            if value is _NotGiven:
                if arg.required:
                    raise CSNotGivenError(arg)
                else:
                    value = arg.default_value

            locals[arg.name] = value

        # varargs
        if self.has_varargs:
            locals[self.varargs_name] = args[len(self.pos_args):]

        # kwargs
        if self.has_kwargs:
            locals[self.kwargs_name] = kwargs

        return locals

    def is_match_amount(self, *args, **kwargs):
        """
        Would a function call with these arguments succeed, based solely on
        number and "keywordnessity" or parameters?
        """
        if len(args) > len(self.pos_args):
            if not self.has_varargs:
                return False  # *args expected

        if len(args) < self.count_required_positionals():
            return False  # Not enough posits

        if len(kwargs) > 0 and not self.has_kwargs:
            return False  # kwargs expected

        return True


def __typeinfo_to_tuple_of_types(typeinfo, operator=type):
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
                new_tup.extend(__typeinfo_to_tuple_of_types(elem))
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

    except TypeError as e:   # must be a typing.* annotation
        if type_ == Callable:
            return hasattr(var, '__call__')
        elif type_ == Iterable:
            return hasattr(var, '__iter__')
        elif type_ == Sequence:
            return hasattr(var, '__iter__') and hasattr(var, '__getattr__') and hasattr(var, '__len__')
        elif type_ == Mapping:
            return hasattr(var, '__getitem__')

        return type(var) == type_

    return False


def _do_if_not_type(var, type_, fun='default'):

    if type_ in ((type(None), ), ) and (fun == 'default'):
        return None

    if type_ in (None, (None, ), 'self'):
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

    t_args = [(__typeinfo_to_tuple_of_types(x) if x is not None else None)
              for x in t_args]

    t_retarg = t_kwargs.get('returns', None)
    is_mandatory = t_kwargs.get('mandatory', False)

    if t_retarg is not None:
        t_retarg = __typeinfo_to_tuple_of_types(t_retarg)

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

    t_args = [(__typeinfo_to_tuple_of_types(x, operator=__NOP))
              for x in t_args]

    def argify(args):
        return [_do_if_not_type(argument, typedescr) \
                        for argument, typedescr in six.moves.zip_longest(args, t_args)]

    t_retarg = t_kwargs.get('returns', None)

    t_retarg = __typeinfo_to_tuple_of_types(t_retarg, operator=__NOP)

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
        return __typeinfo_to_tuple_of_types(s, operator=operator)

    t_args_t = [sselector(x, 0) for x in t_args]
    t_args_c = [sselector(x, 1, operator=__NOP) for x in t_args]

    def argify(args):
        return [_do_if_not_type(argument, typedescr) \
                        for argument, typedescr in six.moves.zip_longest(args, t_args_c)]

    t_retarg = t_kwargs.get('returns', None)
    t_retarg_t = sselector(t_retarg, 0, pt=tuple)
    t_retarg_c = sselector(t_retarg, 1, operator=__NOP, pt=tuple)

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
            precond = __TRUE
        elif isinstance(t_op, six.string_types):
            q = dict(globals())
            exec('_precond = lambda x: '+t_op, q)
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
                for arg, precond in six.moves.zip_longest(args, tn_ops, fillvalue=__TRUE):
                    print(arg, precond, precond.__doc__)
                    if not precond(arg):
                        raise PreconditionError('Argument of value %s failed precondition check' % (arg, ))
            return fun(*args, **kwargs)
        return inner
    return outer


def for_argument(*t_ops, **t_kwops):
    t_ops = [__NOP if op == 'self' else op for op in t_ops]

    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method
            assert len(args) >= len(t_ops)
            return fun(*((__NOP if op is None else op)(arg) for arg, op in six.moves.zip_longest(args, t_ops)),
                       **{k: t_kwops.get(k, __NOP)(v) for k, v in kwargs.items()})
        return inner
    return outer
