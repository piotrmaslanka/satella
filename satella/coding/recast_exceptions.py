import typing as tp
import threading
from .decorators import wraps

__all__ = [
    'rethrow_as',
    'silence_excs',
    'catch_exception'
]

ExcType = tp.Type[Exception]
T = tp.TypeVar('T')


def silence_excs(*exc_types: ExcType, returns=None):
    """
    Silence given exception types.

    Can be either a decorator or a context manager.

    If you are using it as a decorator, you can specify what value should the function return
    by using the returns kwarg:

    >>> @silence_excs(KeyError, returns=5)
    >>> def returns_5():
    >>>     raise KeyError()
    >>> assert returns_5() == 5
    """
    return rethrow_as(exc_types, None, returns=returns)


class rethrow_as:
    """
    Transform some exceptions into others.

    Either a decorator or a context manager

    New exception will be created by calling exception to transform to with
    repr of current one.

    You can also provide just two exceptions, eg.

    >>> rethrow_as(NameError, ValueError)

    You can also provide a pairwise translation, eg. from NameError to ValueError and from OSError
    to IOError

    >>> rethrow_as((NameError, ValueError), (OSError, IOError))

    If the second value is a None, exception will be silenced.
    """
    __slots__ = ('mapping', 'exception_preprocessor', 'returns', '__exception_remapped')

    def __init__(self, *pairs: tp.Union[ExcType, tp.Tuple[ExcType, ExcType]],
                 exception_preprocessor: tp.Optional[tp.Callable[[Exception], str]] = repr,
                 returns=None):
        """
        Pass tuples of (exception to catch - exception to transform to).

        :param exception_preprocessor: other callable/1 to use instead of repr.
            Should return a str, a text description of the exception
        :param returns: what value should the function return if this is used as a decorator
        """
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
                return self.returns
            else:
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
                    else:
                        raise to(self.exception_preprocessor(exc_val))


def catch_exception(exc_class: tp.Union[ExcType, tp.Tuple[ExcType]],
                    clb: tp.Callable[[], T],
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

    :param exc_class: Exception classes to catch
    :param clb: callable/0 to call to raise the exception
    :param return_instead: what to return instead of the function result if it didn't end in an
        exception
    :param return_value_on_no_exception: whether to return the function result if exception didn't
        happen
    :raises ValueError: an exception was not thrown
    :raises TypeError: a different exception was thrown that the one we're catchin
    """
    try:
        result = clb()
    except exc_class as e:
        return e
    except Exception as e:
        raise TypeError('%s was thrown instead' % (e,))

    if return_instead is not None:
        return return_instead

    if return_value_on_no_exception:
        return result

    raise ValueError('Callable executed without error')
