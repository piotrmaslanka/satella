from __future__ import annotations

import functools
import inspect
import operator
import typing as tp
from inspect import Parameter

from satella.coding.structures import frozendict



# Taken from https://stackoverflow.com/questions/28237955/same-name-for-classmethod-and-
# instancemethod
class class_or_instancemethod(classmethod):
    """
    A decorator to make your methods both classmethods (they will receive an instance of type
    as their first argument) or normal methods (they will receive an instance of their type).

    Use like:

    >>> class MyClass:
    >>>     @class_or_instancemethod
    >>>     def method(self_or_cls):
    >>>         if isinstance(self_or_cls, MyClass):
    >>>             # method code
    >>>         else:
    >>>             # classmethod code
    """

    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)


class TypeSignature(inspect.Signature):

    __slots__ = ()

    def __init__(self, t_sign: inspect.Signature):
        self._return_annotation = t_sign._return_annotation
        self._parameters = t_sign._parameters

    @staticmethod
    def from_fun(fun):
        return TypeSignature(inspect.Signature.from_callable(fun))

    def can_be_called_with_args(self, *args, **kwargs) -> bool:
        called = self._bind(*args, **kwargs)
        return all(issubclass(self.signature.parameters.get(arg_name, NONEARGS)._annotation, arg_value)
                   for arg_name, arg_value in called.items())

    def is_more_generic_than(self, b: TypeSignature) -> bool:
        if self == {}:
            for key in self:
                key1 = self[key]
                key2 = b.get(key, None)
                if key2 is None:
                    return key2 == {}

                if key2.is_more_generic_than(key1):
                    return False
        return True

    def __lt__(self, other: TypeSignature) -> bool:
        return self.is_more_generic_than(other)

    def matches(self, *args, **kwargs) -> bool:
        """
        Does this invocation match this signature?
        """
        bound_args = self.bind(*args, **kwargs)
        bound_args.apply_defaults()
        for param_name, param_value in bound_args.arguments.items():
            if isinstance(param_value, self._parameters[param_name].annotation):
                continue
            else:
                return False
        return True


class overload:
    """
    A class used for method overloading.

    .. warning::

       This feature is scheduled for an overhaul and may not work as promised. Keep that in mind.

    Note that methods can be only overloaded by their positional, or positional-and-keyword
    arguments. Overload distinguishment will be done at the level of positional arguments only.

    Note that typing checks will be done via isinstance().

    Use like this:

    >>> @overload
    >>> def what_type(x: str):
    >>>     print('String')
    >>> @what_type.overload
    >>> def what_type(x: int):
    >>>     print('Int')

    Note that this instance's __wrapped__ will refer to the first function.
    TypeError will be called if no signatures match arguments.
    """

    def __init__(self, fun: tp.Callable):
        self.type_signatures_to_functions = {TypeSignature.from_fun(fun): fun}
        if hasattr(fun, '__doc__'):
            self.__doc__ = fun.__doc__
        self.__wrapped__ = fun
        self.history_list = []

    def overload(self, fun):
        """
        :raises ValueError: this signature already has an overload
        """
        sign = TypeSignature.from_fun(fun)
        if sign in self.type_signatures_to_functions:
            raise TypeError('Method of this signature is already overloaded with %s' % (fun,))
        self.type_signatures_to_functions[sign] = fun
        return self

    def __call__(self, *args, **kwargs):
        """
        Call one of the overloaded functions.

        :raises TypeError: no type signature given
        """
        matchings = []
        for sign, fun in self.type_signatures_to_functions.items():
            print('Matching %s against %s', sign, fun)
            if sign.matches(*args, **kwargs):
                matchings.append((sign, fun))
            else:
                print('Did not score a math between %s:%s and %s', args, kwargs, )
        matchings.sort()
        print(matchings)
        if not matchings:
            raise TypeError('No matching entries!')
        else:
            return matchings[-1][1](*args, **kwargs)     # call the most specific function you could find
