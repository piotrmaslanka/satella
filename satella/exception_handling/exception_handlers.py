import types
import typing as tp
import warnings
from abc import abstractmethod

__all__ = [
    'BaseExceptionHandler',
    'FunctionExceptionHandler',
    'exception_handler',
    'ALWAYS_FIRST',
    'ALWAYS_LAST',
    'NORMAL_PRIORITY',
    'ExceptionHandlerCallable'
]

ALWAYS_FIRST = -1000
NORMAL_PRIORITY = 0
ALWAYS_LAST = 1000

ExceptionHandlerCallable = tp.Callable[[type, BaseException, types.TracebackType],
                                       tp.Union[tp.Sequence[bool], bool]]


class BaseExceptionHandler:
    __slots__ = ('priority',)

    def __init__(self, priority=NORMAL_PRIORITY):
        """
        Instantiate an exception handler with provided priority.
        Handlers with smaller priorities run sooner.

        :param priority: Priority to use for this handler
        """
        self.priority = priority

    def install(self) -> 'BaseExceptionHandler':
        """
        Register this handler to run upon exceptions
        """
        from .global_eh import GlobalExcepthook
        GlobalExcepthook().add_hook(self)
        return self

    def uninstall(self):
        """
        Unregister this handler to run on exceptions
        """
        from .global_eh import GlobalExcepthook
        GlobalExcepthook().remove_hook(self)

    @abstractmethod
    def handle_exception(self, type_: tp.Callable[[type, BaseException, types.TracebackType], None],
                         value,
                         traceback: types.TracebackType) -> tp.Optional[bool]:
        """
        Return True to intercept the exception, so that it won't be propagated to other handlers.
        """
        pass


class FunctionExceptionHandler(BaseExceptionHandler):
    """
    A exception handler to make callables of given signature into Satella's exception handlers.

    Your exception handler must return a bool, whether to intercept the exception and not
    propagate it.
    """
    __slots__ = ('fun',)

    def __init__(self, fun: ExceptionHandlerCallable, priority: int = NORMAL_PRIORITY):
        super().__init__(priority)
        self.fun = fun

    def handle_exception(self, type_, value, traceback):
        if type_ == SystemExit:
            return
        val = self.fun(type_, value, traceback)
        if isinstance(val, tp.Sequence):
            val = any(val)
        return val


def exception_handler(priority: int = NORMAL_PRIORITY):
    """
    Convert a callable to an FunctionExceptionHandler. Usage

    >>> @exception_handler(priority=-10)
    >>> def handle_exc(type_, val, traceback):
    >>>     ...

    You can use also:

    >>> @exception_handler
    >>> def handle_exc(type_, val, traceback):
    >>>     ...

    The default priority is 0. But this way of calling it is not recommended, and will
    result in a UserWarning.

    :return: ExceptionHandler instance
    """

    if not isinstance(priority, int):
        warnings.warn('Please specify priority, using default of 0', UserWarning)
        return FunctionExceptionHandler(priority, priority=NORMAL_PRIORITY)

    def outer(fun: ExceptionHandlerCallable) -> FunctionExceptionHandler:
        return FunctionExceptionHandler(fun, priority=priority)

    return outer
