import typing as tp

from satella.coding.typing import ExceptionList


class expect_exception:
    """
    A context manager to use as following:

    >>> a = {'test': 2}
    >>> with expect_exception(KeyError, ValueError, 'KeyError not raised'):
    >>>     a['test2']

    If other exception than the expected is raised, it is passed through

    :param exc_to_except: a list of exceptions or a single exception to expect
    :param else_raise: raise a particular exception if no exception is raised.
        This should be a callable that accepts provided args and kwargs and returns
        an exception instance.
    :param args: args to provide to constructor
    :param kwargs: kwargs to provide to constructor
    """
    __slots__ = 'exc_to_except', 'else_raise', 'else_raise_args', 'else_raise_kwargs'

    def __init__(self, exc_to_except: ExceptionList, else_raise: tp.Type[Exception],
                 *args, **kwargs):
        self.exc_to_except = exc_to_except
        self.else_raise = else_raise
        self.else_raise_args = args
        self.else_raise_kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise self.else_raise(*self.else_raise_args, **self.else_raise_kwargs)
        elif not isinstance(exc_val, self.exc_to_except):
            return False
        return True
