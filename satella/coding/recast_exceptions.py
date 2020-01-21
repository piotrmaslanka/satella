import functools
import typing as tp

__all__ = [
    'rethrow_as',
    'silence_excs',
    'catch_exception'
]


def silence_excs(*exc_types):
    """
    Silence given exception types.

    Can be either a decorator or a context manager
    """
    return rethrow_as(exc_types, None)


class rethrow_as:
    """
    Transform some exceptions into others.

    Either a decorator or a context manager

    New exception will be created by calling exception to transform to with
    repr of current one.

    You can also provide just two exceptions, eg.

    >>> rethrow_as(NameError, ValueError)

    You can also provide a pairwise translation, eg. from NameError to ValueError and from OSError to IOError

    >>> rethrow_as((NameError, ValueError), (OSError, IOError))

    If the second value is a None, exception will be silenced.
    """

    def __init__(self, *pairs,
                 exception_preprocessor: tp.Optional[tp.Callable[[Exception], str]] = None):
        """
        Pass tuples of (exception to catch - exception to transform to).

        :param exception_preprocessor: other callable/1 to use instead of repr.
            Should return a str, a text description of the exception
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

    def __call__(self, fun: tp.Callable) -> tp.Any:
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            with self:
                return fun(*args, **kwargs)

        return inner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            for from_, to in self.mapping:
                if issubclass(exc_type, from_):
                    if to is None:
                        return True
                    else:
                        raise to(self.exception_preprocessor(exc_val))


returning = tp.TypeVar('T')


def catch_exception(exc_class: tp.Union[tp.Type[Exception], tp.Tuple[tp.Type[Exception]]],
                    callable: tp.Callable[[], returning],
                    return_instead: tp.Optional[returning] = None,
                    return_value_on_no_exception: bool = False) -> tp.Union[Exception, returning]:
    """
    Catch exception of given type and return it. Functionally equivalent to:

    >>> try:
    >>>     callable()
    >>> except exc_class as e:
    >>>     result = e

    :param exc_class: Exception classes to catch
    :param callable: callable/0 to call to obtain it
    :param return_instead: what to return instead of the function result if it didn't end in an exception
    :param return_value_on_no_exception: whether to return the function result if exception didn't happen
    :raises ValueError: an exception was not thrown
    :raises TypeError: a different exception was thrown that the one we're catchin
    """
    try:
        result = callable()
    except exc_class as e:
        return e
    except Exception as e:
        raise TypeError('%s was thrown instead' % (e,))

    if return_instead is not None:
        return return_instead

    if return_value_on_no_exception:
        return result

    raise ValueError('Callable executed without error')
