import functools
import typing as tp

__all__ = [
    'rethrow_as',
    'silence_excs'
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
