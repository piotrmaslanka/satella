import typing as tp

T = tp.TypeVar('T')
Iteratable = tp.Union[tp.Iterator[T], tp.Iterable[T]]
U = tp.TypeVar('U')
V = tp.TypeVar('V')
K = tp.TypeVar('K')
Number = tp.Union[int, float]
NoArgCallable = tp.Callable[[], T]

ExceptionClassType = tp.Type[Exception]

__all__ = ['Iteratable', 'T', 'U', 'V', 'K', 'Number', 'ExceptionClassType',
           'NoArgCallable']
