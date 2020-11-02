import typing as tp
from concurrent.futures import Future
from threading import Thread

from satella.coding.decorators.decorators import wraps
from satella.coding.sequences.sequences import infinite_iterator
from satella.coding.typing import T


def run_as_future(fun):
    """
    A decorator that accepts a function that should be executed in a separate thread,
    and a Future returned instead of it's result, that will enable to watch the function for
    completion.

    The created thread will be non-demonic

    Example usage:

    >>> @run_as_future
    >>> def parse_a_file(x: str):
    >>>     ...
    >>> fut = parse_a_file('test.txt')
    >>> result = fut.result()
    """

    @wraps(fun)
    def inner(*args, **kwargs):
        fut = Future()
        fut.set_running_or_notify_cancel()

        def separate_target():
            try:
                fut.set_result(fun(*args, **kwargs))
            except Exception as e:
                fut.set_exception(e)

        Thread(target=separate_target).start()
        return fut

    return inner


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
