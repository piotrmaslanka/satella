import logging
import math
import typing as tp

from satella.coding.decorators.decorators import wraps
from satella.coding.recast_exceptions import rethrow_as
from satella.coding.typing import T

logger = logging.getLogger(__name__)

_SETTABLE_KEYS = {'_Proxy__obj', '_Proxy__wrap_operations'}
Number = tp.Union[float, int]


def wrap_operation(fun):
    @wraps(fun)
    def inner(self: 'Proxy', *args, **kwargs):
        result = fun(self, *args, **kwargs)
        if self._Proxy__wrap_operations:
            result = self.__class__(result)
        return result

    return inner


class Proxy(tp.Generic[T]):
    """
    A base class for classes that try to emulate some other object.

    They will intercept all calls and place them on the target object.

    Note that in-place operations will return the Proxy itself, whereas simple addition will shed
    this proxy, returning object wrapped plus something.

    Only __isinstance__ check is not overridden, due to Python limitations.

    Please access this object in your descendant classes via

    >>> getattr(self, '_Proxy__obj')

    Please note that this class does not overload the descriptor protocol,
    not the pickle interface!

    Note that this overloads __repr__, __str__ and __dir__, which may prove confusing.
    Handle this in your descendant classes.

    If wrap_operations is set, the following code will be executed on the result:

    >>> a = a.__add__(b)
    >>> return self.__class__(a)

    Wrapped operations include all arithmetic operations and bitwise operations,
    except for divmod, but including concat, rounding, truncing and ceiling.

    :param object_to_wrap: object to wrap
    :param wrap_operations: whether results of operations returning something else should be
        also proxied.
    """
    __slots__ = ('__obj', '__wrap_operations')

    def __init__(self, object_to_wrap: T, wrap_operations: bool = False):
        self.__obj = object_to_wrap  # type: T
        self.__wrap_operations = wrap_operations  # type: bool

    def __call__(self, *args, **kwargs):
        return self.__obj(*args, **kwargs)

    def __getitem__(self, item):
        return self.__obj[item]

    def __setitem__(self, key, value) -> None:
        self.__obj[key] = value

    def __delitem__(self, key) -> None:
        del self.__obj[key]

    def __setattr__(self, key, value) -> None:
        if key in _SETTABLE_KEYS:
            super().__setattr__(key, value)
        else:
            setattr(self.__obj, key, value)

    def __getattr__(self, item):
        return getattr(self.__obj, item)

    def __delattr__(self, item) -> None:
        delattr(self.__obj, item)

    def __int__(self) -> int:
        return int(self.__obj)

    @rethrow_as(AttributeError, TypeError)
    def __float__(self) -> float:
        return float(self.__obj)

    @rethrow_as(AttributeError, TypeError)
    def __complex__(self) -> complex:
        return complex(self.__obj)

    def __str__(self) -> str:
        return str(self.__obj)

    @wrap_operation
    def __add__(self, other):
        return self.__obj + other

    def __iadd__(self, other) -> 'Proxy':
        self.__obj += other
        return self

    @wrap_operation
    def __sub__(self, other):
        return self.__obj - other

    def __isub__(self, other) -> 'Proxy':
        self.__obj -= other
        return self

    @wrap_operation
    def __mul__(self, other):
        return self.__obj * other

    def __divmod__(self, other) -> tp.Tuple[Number, Number]:
        return divmod(self.__obj, other)

    @wrap_operation
    def __floordiv__(self, other):
        return self.__obj // other

    def __rdivmod__(self, other):
        return divmod(other, self.__obj)

    @wrap_operation
    def __truediv__(self, other):
        return self.__obj / other

    def __imul__(self, other) -> 'Proxy':
        self.__obj *= other
        return self

    def __itruediv__(self, other) -> 'Proxy':
        self.__obj /= other
        return self

    def __ifloordiv__(self, other) -> 'Proxy':
        self.__obj //= other
        return self

    @wrap_operation
    def __rshift__(self, other):
        return self.__obj >> other

    @wrap_operation
    def __lshift__(self, other):
        return self.__obj << other

    def __ilshift__(self, other) -> 'Proxy':
        self.__obj <<= other
        return self

    def __irshift__(self, other) -> 'Proxy':
        self.__obj >>= other
        return self

    def __iter__(self) -> tp.Iterator:
        return iter(self.__obj)

    def __len__(self) -> int:
        return len(self.__obj)

    def __contains__(self, item) -> bool:
        return item in self.__obj

    def __hash__(self) -> int:
        return hash(self.__obj)

    def __eq__(self, other) -> bool:
        return self.__obj == other

    def __ne__(self, other) -> bool:
        return self.__obj != other

    def __or__(self, other):
        return self.__obj | other

    def __and__(self, other):
        return self.__obj & other

    def __le__(self, other) -> bool:
        return self.__obj <= other

    def __lt__(self, other) -> bool:
        return self.__obj < other

    def __ge__(self, other) -> bool:
        return self.__obj >= other

    def __gt__(self, other) -> bool:
        return self.__obj > other

    def __enter__(self):
        return self.__obj.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__obj.__exit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        return repr(self.__obj)

    def __oct__(self) -> str:
        return oct(self.__obj)

    def __hex__(self) -> str:
        return hex(self.__obj)

    @wrap_operation
    def __abs__(self):
        return abs(self.__obj)

    def __bool__(self) -> bool:
        return bool(self.__obj)

    def __format__(self, format_spec):
        return self.__obj.__format__(format_spec)

    def __next__(self):
        return next(self.__obj)

    @wrap_operation
    def __xor__(self, other):
        return self.__obj ^ other

    @wrap_operation
    def __radd__(self, other):
        return other + self.__obj

    @wrap_operation
    def __rsub__(self, other):
        return other - self.__obj

    @wrap_operation
    def __rmul__(self, other):
        return other * self.__obj

    @wrap_operation
    def __rtruediv__(self, other):
        return other / self.__obj

    @wrap_operation
    def __rfloordiv__(self, other):
        return other // self.__obj

    @wrap_operation
    def __rlshift__(self, other):
        return other << self.__obj

    @wrap_operation
    def __rrshift__(self, other):
        return other >> self.__obj

    @wrap_operation
    def __rpow__(self, other):
        return other ** self.__obj

    @wrap_operation
    def __ror__(self, other):
        return other | self.__obj

    @wrap_operation
    def __rand__(self, other):
        return other & self.__obj

    @wrap_operation
    def __rxor__(self, other):
        return other ^ self.__obj

    def __ior__(self, other) -> 'Proxy':
        self.__obj |= other
        return self

    def __iand__(self, other) -> 'Proxy':
        self.__obj &= other
        return self

    def __ixor__(self, other) -> 'Proxy':
        self.__obj ^= other
        return self

    def __await__(self):
        return self.__obj.__await()

    def __aenter__(self):
        return self.__obj.__aenter__()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__obj.__aexit__(exc_type, exc_val, exc_tb)

    def __aiter__(self):
        return self.__obj.__aiter__()

    def __reversed__(self):
        return reversed(self.__obj)

    @wrap_operation
    def __pow__(self, power, modulo=None):
        return pow(self.__obj, power, modulo)

    def __ipow__(self, other) -> 'Proxy':
        self.__obj **= other
        return self

    @wrap_operation
    def __neg__(self):
        return -self.__obj

    @wrap_operation
    def __pos__(self):
        return +self.__obj

    @wrap_operation
    def __invert__(self):
        return ~self.__obj

    @wrap_operation
    def __matmul__(self, other):
        return self.__obj @ other

    def __imatmul__(self, other):
        self.__obj @= other
        return self

    @wrap_operation
    def __rmatmul__(self, other):
        return other @ self.__obj

    def __index__(self) -> int:
        return self.__obj.__index__()

    @wrap_operation
    @rethrow_as(AttributeError, TypeError)
    def __round__(self, n: int = 0):
        return round(self.__obj, n)

    @wrap_operation
    @rethrow_as(AttributeError, TypeError)
    def __trunc__(self):
        if hasattr(self.__obj, '__trunc__'):
            result = self.__obj.__trunc__()
        else:
            result = math.trunc(self.__obj)
        return result

    @wrap_operation
    @rethrow_as(AttributeError, TypeError)
    def __floor__(self):
        if hasattr(self.__obj, '__floor__'):
            result = self.__obj.__floor__()
        else:
            result = math.floor(self.__obj)

        return result

    @wrap_operation
    @rethrow_as(AttributeError, TypeError)
    def __ceil__(self):
        if hasattr(self.__obj, '__ceil__'):
            result = self.__obj.__ceil__()
        else:
            result = math.ceil(self.__obj)
        return result

    def __dir__(self) -> tp.Iterable[str]:
        return dir(self.__obj)

    @wrap_operation
    @rethrow_as(AttributeError, TypeError)
    def __concat__(self, other):
        return self.__obj.__concat__(other)

    @rethrow_as(AttributeError, TypeError)
    def __iconcat__(self, other) -> 'Proxy':
        self.__obj.__iconcat__(other)
        return self

    @rethrow_as(AttributeError, TypeError)
    def __length_hint__(self):
        return self.__obj.__length_hint__()
