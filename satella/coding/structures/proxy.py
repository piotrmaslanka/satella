import logging
import typing as tp

T = tp.TypeVar('T')
logger = logging.getLogger(__name__)


_SETTABLE_KEYS = {'_Proxy__obj', '_Proxy__wrap_operations'}


class Proxy(tp.Generic[T]):
    """
    A base class for classes that try to emulate some other object.

    They will intercept all calls and place them on the target object.

    Note that in-place operations will return the Proxy itself, whereas simple addition will shed
    this proxy, returning object wrapped plus something.

    Note that proxies are considered to be the type of the object that they wrap,
    as well as considered to be of type Proxy.

    :param object_to_wrap: object to wrap
    :param wrap_operations: whether results of operations returning something else should be
        also proxied. This will be done by the following code:
        >>> a = a.__add__(b)
        >>> return self.__class__(a)
        Wrapped operations include ONLY add, sub, mul, all kinds of div.
        If you want logical operations wrapped, file an issue.
    """
    __slots__ = ('__obj', '__wrap_operations')


    def __init__(self, object_to_wrap: T, wrap_operations: bool = False):
        self.__obj = object_to_wrap   # type: T
        self.__wrap_operations = wrap_operations

    def __call__(self, *args, **kwargs):
        return self.__obj(*args, **kwargs)

    def __getitem__(self, item):
        return self.__obj[item]

    def __setitem__(self, key, value):
        self.__obj[key] = value

    def __delitem__(self, key):
        del self.__obj[key]

    def __setattr__(self, key, value):
        if key in _SETTABLE_KEYS:
            super().__setattr__(key, value)
        else:
            setattr(self.__obj, key, value)

    def __getattr__(self, item):
        return getattr(self.__obj, item)

    def __delattr__(self, item):
        delattr(self.__obj, item)

    def __int__(self):
        return int(self.__obj)

    def __float__(self):
        return float(self.__obj)

    def __complex__(self):
        return complex(self.__obj)

    def __str__(self):
        return str(self.__obj)

    def __add__(self, other):
        result = self.__obj + other
        if self.__wrap_operations:
            result = self.__class__(result)
        return result

    def __iadd__(self, other):
        self.__obj += other
        return self

    def __sub__(self, other):
        result = self.__obj - other
        if self.__wrap_operations:
            result = self.__class__(result)
        return result

    def __isub__(self, other):
        self.__obj -= other
        return self

    def __mul__(self, other):
        result = self.__obj * other
        if self.__wrap_operations:
            result = self.__class__(result)
        return result

    def __divmod__(self, other):
        result = divmod(self.__obj, other)
        if self.__wrap_operations:
            result = self.__class__(result)
        return result

    def __floordiv__(self, other):
        result = self.__obj // other
        if self.__wrap_operations:
            result = self.__class__(result)
        return result

    def __truediv__(self, other):
        result = self.__obj / other
        if self.__wrap_operations:
            result = self.__class__(result)
        return result

    def __imul__(self, other):
        self.__obj *= other
        return self

    def __itruediv__(self, other):
        self.obj /= other
        return self

    def __ifloordiv__(self, other):
        self.obj //= other
        return self

    def __ilshift__(self, other):
        self.obj <<= other
        return self

    def __irshift__(self, other):
        self.obj >>= other
        return self

    def __iter__(self):
        return iter(self.__obj)

    def __len__(self):
        return len(self.__obj)

    def __contains__(self, item):
        return item in self.__obj

    def __hash__(self):
        return hash(self.__obj)

    def __eq__(self, other):
        return self.__obj == other

    def __or__(self, other):
        return self.__obj or other

    def __and__(self, other):
        return self.__obj and other

    def __le__(self, other):
        return self.__obj <= other

    def __lt__(self, other):
        return self.__obj < other

    def __ge__(self, other):
        return self.__obj >= other

    def __gt__(self, other):
        return self.__obj > other

    def __enter__(self):
        return self.__obj.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__obj.__exit__(exc_type, exc_val, exc_tb)

    def __repr__(self):
        return repr(self.__obj)

    def __abs__(self):
        return abs(self.__obj)

    def __bool__(self):
        return bool(self.__obj)

    def __format__(self, format_spec):
        return self.__obj.__format__(format_spec)

    def __next__(self):
        return next(self.__obj)

    def __xor__(self, other):
        return self.__obj ^ other
