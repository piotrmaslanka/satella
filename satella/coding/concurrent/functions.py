import typing as tp
from concurrent.futures import Future, wait

from satella.coding.sequences.sequences import infinite_iterator

T = tp.TypeVar('T')


def parallel_execute(callable_: tp.Callable[[T], Future],
                     args: tp.Iterable[T],
                     kwargs: tp.Iterable[dict] = infinite_iterator(return_factory=dict)):
    """
    Execute a number of calls to callable in parallel.

    Callable must be a function that accepts arguments and returns a plain Python future.

    Return will be an iterator that will yield every value of the iterator,
    or return an instance of exception, if any of the calls excepted.

    :param callable_: a callable that returns futures
    :param args: an iterable of arguments to provide to the callable
    :param kwargs: an iterable of keyword arguments to provide to the callable
    :return: an iterator yielding every value (or exception instance if thew) of the future
    """
    futures = [callable_(*arg, **kwarg) for arg, kwarg in zip(args, kwargs)]
    for future in futures:
        try:
            yield future.result()
        except Exception as e:
            yield e
