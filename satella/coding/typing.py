import typing as tp

try:
    from typing import Protocol
except ImportError:
    Protocol = tp.Generic

T = tp.TypeVar('T')
Iteratable = tp.Union[tp.Iterator[T], tp.Iterable[T]]
U = tp.TypeVar('U')
V = tp.TypeVar('V')
K = tp.TypeVar('K')
Number = tp.Union[int, float]
NoArgCallable = tp.Callable[[], T]
Predicate = tp.Callable[[T], bool]

ExceptionClassType = tp.Type[Exception]


class Appendable(Protocol[T]):
    def append(self, item: T) -> None:
        pass


__all__ = ['Iteratable', 'T', 'U', 'V', 'K', 'Number', 'ExceptionClassType',
           'NoArgCallable', 'Appendable', 'Predicate']
