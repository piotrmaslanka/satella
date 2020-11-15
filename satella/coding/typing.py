import typing as tp
from abc import ABCMeta, abstractmethod


T = tp.TypeVar('T')
Iteratable = tp.Union[tp.Iterator[T], tp.Iterable[T]]
U = tp.TypeVar('U')
V = tp.TypeVar('V')
K = tp.TypeVar('K')
KVTuple = tp.Tuple[K, V]
Number = tp.Union[int, float]
NoArgCallable = tp.Callable[[], T]
Predicate = tp.Callable[[T], bool]

ExceptionClassType = tp.Type[Exception]


class ClassComparable(metaclass=ABCMeta):
    @abstractmethod
    def __gt__(self, other: tp.Any) -> bool:
        ...

    @abstractmethod
    def __lt__(self, other: tp.Any) -> bool:
        ...

    @abstractmethod
    def __eq__(self, other: tp.Any) -> bool:
        ...


Comparable = tp.TypeVar('Comparable', bound=ClassComparable)

try:
    from typing import Protocol
except ImportError:
    Protocol = tp.Generic


class Appendable(Protocol[T]):
    def append(self, item: T) -> None:
        ...


__all__ = ['Iteratable', 'T', 'U', 'V', 'K', 'Number', 'ExceptionClassType',
           'NoArgCallable', 'Appendable', 'Predicate', 'KVTuple',
           'Comparable']
