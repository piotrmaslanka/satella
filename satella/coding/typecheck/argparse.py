# coding=UTF-8
from __future__ import print_function, absolute_import, division

import inspect
import itertools
from collections import namedtuple
from copy import copy

from .basics import *

__all__ = [
    '_CSArgument',
    'CSArgument',
    'CSVarargsPlaceholder',
    'CSKwargsPlaceholder',
    'CSBadTypeError', 'CSMultipleValuesGivenError', 'CSNotGivenError', 'CSTypeError',
    'CallSignature'
]

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
        return 'Problem with argument %s' % (self.arg.name,)

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
        return 'Got multiple values for argument %s' % (self.arg.name,)


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
