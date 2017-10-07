# coding=UTF-8
"""
Decorator for debug-time typechecking
"""
from __future__ import print_function, absolute_import, division

import inspect
import itertools
import logging

import six

try:
    import typing
except ImportError:
    from backports import typing
from collections import namedtuple
import functools

logger = logging.getLogger(__name__)

List = typing.List
Tuple = typing.Tuple
Dict = typing.Dict
NewType = typing.NewType
Callable = typing.Callable
Sequence = typing.Sequence
Number = six.integer_types + (float,)
TypeVar = typing.TypeVar
Generic = typing.Generic
Mapping = typing.Mapping
Iterable = typing.Iterable
Union = typing.Union
Any = typing.Any
Optional = typing.Optional


# Internal tokens - only instances will be
class _NotGiven(object):
    pass


class _NoDefault(object):
    pass


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
      - varargs_name (Union[str, None]) - name of varargs argument, or None if
        not present
      - kwargs_name (Union[str, None]) - name of kwargs argument, or None if
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


def __typeinfo_to_tuple_of_types(typeinfo):
    if typeinfo == 'self':
        return None
    elif typeinfo is None:
        return (type(None),)
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
                if typedescr is not None:
                    if not isinstance(argument, typedescr):
                        raise TypeError('Got %s, expected %s' % (
                            type(argument), typedescr))

            rt = fun(*args, **kwargs)

            if t_retarg is not None:
                if not isinstance(rt, t_retarg):
                    raise TypeError('Returned %s, expected %s' % (
                        type(rt), t_retarg))

            return rt
        return inner
    return outer
