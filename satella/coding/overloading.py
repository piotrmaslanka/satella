from __future__ import annotations

import inspect
import typing as tp


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
    """
    A type signature.

    You can compare signatures:

    >>> def a(y: object):
    >>>     pass
    >>> def b(y: int):
    >>>     pass
    >>> TypeSignature.from_fun(a) < TypeSignature(b)
    """
    __slots__ = ()

    # pylint: disable=protected-access
    def __init__(self, t_sign: inspect.Signature):
        """
        :param t_sign: a inspect.Signature
        """
        self._return_annotation = t_sign._return_annotation
        self._parameters = t_sign._parameters

    @staticmethod
    def from_fun(fun) -> TypeSignature:
        """Return a type signature from a function"""
        return TypeSignature(inspect.Signature.from_callable(fun))

    def can_be_called_with_args(self, *args, **kwargs) -> bool:
        """Can this type signature be called with following arguments?"""
        called = self._bind(*args, **kwargs)

        # pylint: disable=protected-access
        return all(issubclass(self.signature.parameters.get(arg_name, NONEARGS)._annotation, arg_value)
                   for arg_name, arg_value in called.items())

    def is_more_generic_than(self, b: TypeSignature) -> bool:
        """Is this type signature more generic than an other?"""
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
            if not isinstance(param_value, self._parameters[param_name].annotation):
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
    >>> what_type(5)
    >>> what_type('string')

    Note that this instance's __wrapped__ will refer to the first function.
    TypeError will be called if no signatures match arguments.
    """

    def __init__(self, fun: tp.Callable):
        self.type_signatures_to_functions = {TypeSignature.from_fun(fun): fun}
        if hasattr(fun, '__doc__'):
            self.__doc__ = fun.__doc__
        self.__wrapped__ = fun

    @property
    def all_functions(self) -> tp.Iterable[object]:
        """Return a list of all functions registered within this overload"""
        return self.type_signatures_to_functions.values()

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
        matching = []
        for sign, fun in self.type_signatures_to_functions.items():
            if sign.matches(*args, **kwargs):
                matching.append((sign, fun))
        matching.sort()     # This sorting should result in most precise class at the end of the list
        if not matching:
            raise TypeError('No matching entries!')
        else:
            return matching[-1][1](*args, **kwargs)  # call the most specific function you could find
