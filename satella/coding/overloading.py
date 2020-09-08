import typing as tp
import inspect
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
            raise ValueError('Method of this signature is already overloaded with %s' % (f, ))
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



