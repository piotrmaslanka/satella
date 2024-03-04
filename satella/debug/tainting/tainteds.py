from __future__ import annotations

import functools
import typing as tp

from satella.coding.typing import T


def might_accept_tainted(taint_result: bool = False):
    """
    For methods that might accept a tainted value during execution
    
    This both unpacks your first argument if is was a TaintedObject, you'll receive it's value
    :param taint_result: result will be tainted
    """

    def outer(fun):
        @functools.wraps(fun)
        def inner(self, *args):
            if len(args) > 0:
                args = access_tainted(args[0]), *args[1:]
            p = fun(self, *args)
            if taint_result:
                return taint(p)
            else:
                return p

        return inner

    return outer


class TaintedObject(tp.Generic[T]):
    __slots__ = '__environment', '__v'

    def __new__(cls, v):
        if isinstance(v, TaintedObject):
            return v
        return object.__new__(cls)

    def __init__(self, v: T):
        from .environment import TaintingEnvironment
        if isinstance(v, TaintedObject):
            # all is already set correctly for this object and it will be returned
            return
        self.__environment = TaintingEnvironment.get_session_in_progress()
        self.__v = v
        if isinstance(v, tp.MutableSequence):
            for i in range(len(v)):
                self.__v[i] = taint(v[i])
        else:
            try:
                if isinstance(v, tp.MutableMapping):
                    dict_to_transform = v
                else:
                    dict_to_transform = v.__dict__
                for key in dict_to_transform:
                    dict_to_transform[key] = taint(dict_to_transform[key])
            except AttributeError:
                pass  # must have been a primitive type

    def __setattr__(self, key: str, value: tp.Any):
        if key == '_TaintedObject__environment' or key == '_TaintedObject__v':
            super().__setattr__(key, value)
        else:
            super().__setattr__(key, taint(value))

    def __iter__(self) -> tp.Iterator[TaintedObject[T]]:
        for item in self.__v:
            yield taint(item)

    def __next__(self) -> TaintedObject[T]:
        return taint(next(self.__v))

    @might_accept_tainted()
    def __str__(self) -> str:  # it must be a str otherwise Python will complain
        return str(self.__v)

    def __call__(self, *args, **kwargs):
        return taint(self.__v(*args, **kwargs))

    @might_accept_tainted(taint_result=True)
    def __repr__(self) -> str:
        return '%s TAINTED' % str(self.__v)

    @might_accept_tainted(taint_result=True)
    def __getattr__(self, item: str) -> TaintedObject[T]:
        return getattr(self.__v, item)

    def __len__(self) -> int:  # This has to return an int otherwise Python will break
        return len(self.__v)

    def __bool__(self) -> bool:  # This has to return a bool otherwise Python will break
        return bool(self.__v)

    def __int__(self) -> int:
        return int(self.__v)

    def __float__(self) -> float:
        return float(self.__v)

    def __enter__(self):
        return taint(self.__v.__enter__())

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__v.__exit__(exc_type, exc_val, exc_tb)

    @might_accept_tainted(taint_result=True)
    def __eq__(self, other) -> bool:
        return self.__v == other

    @might_accept_tainted(taint_result=True)
    def __gt__(self, other) -> bool:
        return self.__v > other

    @might_accept_tainted(taint_result=True)
    def __ge__(self, other) -> bool:
        return self.__v >= other

    @might_accept_tainted(taint_result=True)
    def __lt__(self, other) -> bool:
        return self.__v < other

    @might_accept_tainted(taint_result=True)
    def __le__(self, other) -> bool:
        return self.__v <= other

    @might_accept_tainted(taint_result=True)
    def __add__(self, other) -> TaintedObject:
        return self.__v + other

    @might_accept_tainted(taint_result=True)
    def __radd__(self, other) -> TaintedObject:
        return other + self.__v

    @might_accept_tainted()
    def __iadd__(self, other) -> TaintedObject:
        self.__v += other
        return self

    @might_accept_tainted(taint_result=True)
    def __sub__(self, other) -> TaintedObject:
        return self.__v - other

    @might_accept_tainted()
    def __isub__(self, other) -> TaintedObject:
        self.__v -= other
        return self

    @might_accept_tainted(taint_result=True)
    def __mul__(self, other) -> TaintedObject:
        return self.__v * other

    @might_accept_tainted()
    def __imul__(self, other) -> TaintedObject:
        self.__v *= other
        return self

    def __dir__(self) -> tp.Iterable[str]:
        return dir(self.__v)

    def __hash__(self) -> int:
        return hash(self.__v)

    def __getitem__(self, item: int) -> TaintedObject[T]:
        return taint(self.__v[item])

    def __setitem__(self, key, value: T) -> None:
        self.__v[key] = taint(value)

    def __delitem__(self, key: str) -> None:
        del self.__v[key]


def access_tainted(v: tp.Union[T, TaintedObject[T]]) -> T:
    """
    If v is tainted, this will extract it's value.

    If it is not, v will be returned
    """
    if not isinstance(v, TaintedObject):
        return v
    return getattr(v, '_TaintedObject__v')


def taint(v: T) -> TaintedObject[T]:
    """
    Taints the object if necessary. If already tainted will leave it as is

    :raises RuntimeError: no tainting session in progress
    """
    return v if isinstance(v, TaintedObject) else TaintedObject(v)
