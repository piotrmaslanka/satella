import inspect
import typing as tp
from inspect import Parameter


def extract_type_signature_from(fun: tp.Callable) -> tp.Tuple[type, ...]:
    sign = []
    params = inspect.signature(fun).parameters
    for parameter in params.values():
        if parameter.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            if parameter.annotation == Parameter.empty:
                sign.append(None)
            else:
                sign.append(parameter.annotation)
    return tuple(sign)


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


class overload:
    """
    A class used for method overloading.

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
    """

    def __init__(self, fun: tp.Callable):
        self.type_signatures_to_functions = {
            extract_type_signature_from(fun): fun
        }  # type: tp.Dict[tp.Tuple[type, ...], tp.Callable]
        if hasattr(fun, '__doc__'):
            self.__doc__ = fun.__doc__

    def overload(self, fun):
        """
        :raises ValueError: this signature already has an overload
        """
        sign = extract_type_signature_from(fun)
        if sign in self.type_signatures_to_functions:
            f = self.type_signatures_to_functions[sign]
            raise ValueError('Method of this signature is already overloaded with %s' % (f,))
        self.type_signatures_to_functions[sign] = fun
        return self

    def __call__(self, *args, **kwargs):
        """
        Call one of the overloaded functions.

        :raises TypeError: no type signature matched
        """
        for sign, fun in self.type_signatures_to_functions.items():
            try:
                for type_, arg in zip(sign, args):
                    if type_ is None:
                        continue
                    if not isinstance(arg, type_):
                        raise ValueError()

                return fun(*args, **kwargs)
            except ValueError:
                pass
        raise TypeError('No matching functions found')
