import types
import typing as tp
from abc import abstractmethod

__all__ = [
    'BaseExceptionHandler',
    'FunctionExceptionHandler',
    'exception_handler',
    'ALWAYS_FIRST',
    'ALWAYS_LAST',
    'NORMAL_PRIORITY'
]

ALWAYS_FIRST = -1000
NORMAL_PRIORITY = 0
ALWAYS_LAST = 1000


class BaseExceptionHandler:
    def __init__(self, priority=NORMAL_PRIORITY):
        self.priority = priority

    def install(self):
        from .global_eh import GlobalExcepthook
        GlobalExcepthook().add_hook(self)
        return self

    def uninstall(self):
        from .global_eh import GlobalExcepthook
        GlobalExcepthook().remove_hook(self)

    @abstractmethod
    def handle_exception(self, type_: tp.Optional[type], value,
                         traceback: types.TracebackType) -> tp.Optional[bool]:
        """Return True to intercept the exception. It won't be propagated to other handlers."""
        pass


class FunctionExceptionHandler(BaseExceptionHandler):
    def __init__(self, fun: tp.Callable, priority: int = NORMAL_PRIORITY):
        super(FunctionExceptionHandler, self).__init__(priority)
        self.fun = fun

    def handle_exception(self, type_, value, traceback):
        if type_ == SystemExit:
            return
        return self.fun(type_, value, traceback)


def exception_handler(priority: int = NORMAL_PRIORITY):
    """
    Convert a callable to an FunctionExceptionHandler. Usage

        @exception_handler(priority=-10)
        def handle_exc(type, val, traceback):
            ...

    :return: ExceptionHandler instance
    """

    if not isinstance(priority, int):
        raise TypeError('Did you forget to use it as @exception_handler() ?')

    def outer(fun):
        return FunctionExceptionHandler(fun, priority=priority)

    return outer
