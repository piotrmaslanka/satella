import inspect
import logging
import threading
import typing as tp

from .decorators.decorators import wraps
from .typing import ExceptionClassType, T, NoArgCallable, ExceptionList


def silence_excs(*exc_types: ExceptionClassType, returns=None,
                 returns_factory: tp.Optional[NoArgCallable[tp.Any]] = None):
    """
    Silence given exception types.

    Can be either a decorator or a context manager.

    If you are using it as a decorator, you can specify what value should the function return
    by using the returns kwarg:

    >>> @silence_excs(KeyError, returns=5)
    >>> def returns_5():
    >>>     raise KeyError()
    >>> assert returns_5() == 5

    Or if you want to you can specify a callable that will return the value you want to return

    >>> @silence_excs(KeyError, returns_factory=lambda: 5)
    >>> def returns_5():
    >>>     raise KeyError()
    >>> assert returns_5() == 5

    :raises ValueError: you gave both returns and returns_factory. You can only pass one of them!
    """
    return rethrow_as(exc_types, None, returns=returns, returns_factory=returns_factory)


class log_exceptions:
    """
    Decorator/context manager to log your exceptions into the log.

    The exception will be logged and re-raised.

    Logger will be passed the exception instance as exc_info.

    :param logger: a logger to which the exception has to be logged
    :param severity: a severity level
    :param format_string: a format string with fields:
        - e      : the exception instance itself
        - args   : positional arguments with which the function was called, unavailable if context
                   manager
        - kwargs : keyword arguments with which the function was called, unavailable if context
                   manager
        You can specify additional fields providing the locals_ argument
        Example: "{exc_type} occurred with message {exc_val} with traceback {exc_tb}"
    :param locals_: local variables to add to the format string. args and kwargs will be overwritten
        by this, but e will never be overwritten.
    :param exc_types: logger will log only on those exceptions. Default is None which means
        log on all exceptions
    :param swallow_exception: if True, exception will be swallowed
    """
    __slots__ = 'logger', 'severity', 'format_string', 'locals', 'exc_types', 'swallow_exception'

    def __init__(self, logger: logging.Logger,
                 severity: int = logging.ERROR,
                 format_string: str = '{e}',
                 locals_: tp.Optional[tp.Dict] = None,
                 exc_types: tp.Union[
                     ExceptionClassType, tp.Sequence[ExceptionClassType]] = Exception,
                 swallow_exception: bool = False):
        self.logger = logger
        self.swallow_exception = swallow_exception
        self.severity = severity
        self.format_string = format_string
        self.locals = locals_
        self.exc_types = exc_types

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False if not self.analyze_exception(exc_val, (), {}) else self.swallow_exception
        return False

    def analyze_exception(self, e, args, kwargs) -> bool:
        """Return whether the exception has been logged"""
        if not isinstance(e, self.exc_types):
            return False
        format_dict = {'args': args, 'kwargs': kwargs}
        if self.locals is not None:
            format_dict.update(self.locals)
        format_dict['e'] = e
        self.logger.log(self.severity, self.format_string.format(**format_dict),
                        exc_info=e)
        return True

    def __call__(self, fun):
        if inspect.isgeneratorfunction(fun):
            @wraps(fun)
            def inner(*args, **kwargs):
                # noinspection PyBroadException
                try:
                    yield from fun(*args, **kwargs)
                except Exception as e:      # pylint: disable=broad-except
                    if not self.analyze_exception(e, args, kwargs) or not self.swallow_exception:
                        raise

            return inner
        else:
            @wraps(fun)
            def inner(*args, **kwargs):
                # noinspection PyBroadException
                try:
                    return fun(*args, **kwargs)
                except Exception as e:      # pylint: disable=broad-except
                    if not self.analyze_exception(e, args, kwargs) or not self.swallow_exception:
                        raise

            return inner


# noinspection PyPep8Naming
class reraise_as:
    """
    Transform some exceptions into others.

    Either a decorator or a context manager

    New exception will be created by calling exception to transform to with
    repr of current one.

    You can also provide just two exceptions, eg.

    >>> reraise_as(NameError, ValueError, 'a value error!')

    You can also provide a catch-all:

    >>> reraise_as((NameError, ValueError), OSError, 'an OS error!')

    New exception will be raised from the one caught!

    .. note:: This checks if exception matches directly via :code:`isinstance`, so defining
        your own subclassing hierarchy by :code:`__isinstance__` or :code:`__issubclass__`
        will work here.

    This is meant as an improvement of :class:`~satella.coding.rethrow_as`

    :param source_exc: source exception or a tuple of exceptions to catch
    :param target_exc: target exception to throw. If given a None, the exception will
        be silently swallowed.
    :param args: arguments to constructor of target exception
    :param kwargs: keyword arguments to constructor of target exception
    """
    __slots__ = 'source', 'target_exc', 'args', 'kwargs'

    def __init__(self, source_exc: ExceptionList,
                 target_exc: tp.Optional[ExceptionClassType], *args, **kwargs):
        self.source = source_exc
        self.target_exc = target_exc
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fun: tp.Callable) -> tp.Callable:
        @wraps(fun)
        def inner(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except Exception as e:          # pylint: disable=broad-except
                if isinstance(e, self.source):
                    if self.target_exc is not None:
                        raise self.target_exc(*self.args, **self.kwargs) from e
                    return
                raise

        return inner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            if isinstance(exc_val, self.source):
                if self.target_exc is None:
                    return True
                raise self.target_exc(*self.args, **self.kwargs) from exc_val
        return False


# noinspection PyPep8Naming
class rethrow_as:
    """
    Transform some exceptions into others.

    Either a decorator or a context manager

    New exception will be created by calling exception to transform to with
    repr of current one.

    .. note:: This checks if exception matches directly via :code:`isinstance`, so defining
        your own subclassing hierarchy by :code:`__isinstance__` or :code:`__issubclass__`
        will work here.

    You can also provide just two exceptions, eg.

    >>> rethrow_as(NameError, ValueError)

    You can also provide a pairwise translation, eg. from NameError to ValueError and from OSError
    to IOError

    >>> rethrow_as((NameError, ValueError), (OSError, IOError))

    If the second value is a None, exception will be silenced.

    Pass tuples of (exception to catch - exception to transform to).

    .. warning:: Try to use :class:`~satella.coding.reraise_as` instead.
        However, during to richer set of switches and capability to return a value
        this is not deprecated.

    :param exception_preprocessor: other callable/1 to use instead of repr.
        Should return a str, a text description of the exception
    :param returns: what value should the function return if this is used as a decorator
    :param returns_factory: a callable that returns the value this function should return is this
        is used as as decorator
    :raises ValueError: you specify both returns and returns_factory
    """
    __slots__ = 'mapping', 'exception_preprocessor', 'returns', '__exception_remapped', 'returns_factory'

    def __init__(self, *pairs: ExceptionList,
                 exception_preprocessor: tp.Optional[tp.Callable[[Exception], str]] = repr,
                 returns=None,
                 returns_factory: tp.Optional[NoArgCallable[tp.Any]] = None):
        try:
            a, b = pairs  # throws ValueError
            op = issubclass(b, BaseException)  # throws TypeError
        except TypeError:
            op = b is None
        except ValueError:
            op = False

        if op:
            pairs = [pairs]

        self.mapping = list(pairs)
        self.exception_preprocessor = exception_preprocessor or repr
        self.returns = returns
        self.returns_factory = returns_factory

        if self.returns is not None and self.returns_factory is not None:
            raise ValueError('You can specify only one of (returns, returns_factory)')

        # this is threading.local because two threads may execute the same function at the
        # same time, and exceptions from one function would leak to another
        self.__exception_remapped = threading.local()

    def __call__(self, fun: tp.Callable) -> tp.Callable:
        @wraps(fun)
        def inner(*args, **kwargs):
            with self:
                v = fun(*args, **kwargs)
            if self.__exception_remapped.was_raised:
                # This means that the normal flow of execution was interrupted
                if self.returns is not None:
                    return self.returns
                elif self.returns_factory is not None:
                    return self.returns_factory()
                return
            return v

        return inner

    def __enter__(self):
        self.__exception_remapped.was_raised = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            for from_, to in self.mapping:
                if issubclass(exc_type, from_):
                    self.__exception_remapped.was_raised = True
                    if to is None:
                        return True
                    raise to(self.exception_preprocessor(exc_val))


def raises_exception(exc_class: tp.Union[ExceptionClassType, tp.Tuple[ExceptionClassType, ...]],
                     clb: NoArgCallable[None]) -> bool:
    """
    Does the callable raise a given exception?
    """
    try:
        clb()
    except exc_class:
        return True
    return False


def catch_exception(exc_class: tp.Union[ExceptionClassType, tp.Tuple[ExceptionClassType, ...]],
                    clb: NoArgCallable[tp.Optional[T]],
                    return_instead: tp.Optional[T] = None,
                    return_value_on_no_exception: bool = False) -> tp.Union[Exception, T]:
    """
    Catch exception of given type and return it. Functionally equivalent to:

    >>> try:
    >>>     v = clb()
    >>>     if return_value_on_no_exception:
    >>>         return v
    >>> except exc_class as e:
    >>>     if return_instead:
    >>>         return return_instead
    >>>     return e

    If a different class of exception is caught, it will be propagated.

    :param exc_class: Exception classes to catch
    :param clb: callable/0 to call to raise the exception
    :param return_instead: what to return instead of the function result if it didn't end in an
        exception
    :param return_value_on_no_exception: whether to return the function result if exception didn't
        happen
    :raises ValueError: an exception was not thrown
    """
    try:
        result = clb()
    except exc_class as e:
        return e

    if return_instead is not None:
        return return_instead

    if return_value_on_no_exception:
        return result

    raise ValueError('Callable executed without error')
