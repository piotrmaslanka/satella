import logging
import typing
import functools
logger = logging.getLogger(__name__)

__all__ = ['treat_result_with']


def treat_result_with(callable):
    """
    Before this function returns, process it's result with callable

    @treat_result_with(callable)
    def fun(*args, **kwargs):
        ...

    is equivalent to:
    def fun(*args, **kwargs):
        ...

    fun = lambda *args, **kwargs: callable(fun(*args, **kwargs))
    """
    def inner(f):
        @functools.wraps(f)
        def inner2(*args, **kwargs):
            return callable(f(*args, **kwargs))
        return inner2
    return inner
