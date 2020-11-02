import typing as tp
from concurrent.futures import Executor

from satella.coding.concurrent.futures.futures import wrap_if


def call_in_future(executor: Executor, function: tp.Callable,
                   *args, **kwargs) -> tp.Callable[[], 'Future']:
    """
    Return a callable, whose calling will schedule function to be executed on a target Executor.

    The returned function will accept any number of arguments and keyword arguments, but will simply
    ignore them.

    :param executor: executor to run at
    :param function: callable to schedule
    :param args: arguments to provide to the callable
    :param kwargs: keyword arguments to provide to the callable
    :return: a callable, calling which will schedule function to run at executor. Calling this callable
        will return the Future for that function
    """

    def inner(*my_args, **my_kwargs):
        return wrap_if(executor.submit(function, *args, **kwargs))

    return inner
