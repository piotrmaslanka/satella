import itertools
import typing as tp

from satella.coding.decorators.decorators import wraps
from satella.coding.typing import ExceptionClassType


def retry(times: tp.Optional[int] = None,
          exc_classes: tp.Union[ExceptionClassType, tp.Tuple[ExceptionClassType, ...]] = Exception,
          on_failure: tp.Callable[[Exception], None] = lambda e: None,
          swallow_exception: bool = True):
    """
    A decorator retrying given operation, failing it when an exception shows up.

    Essentially this:

    >>> @retry(3, RuntimeError)
    >>> def do_op():
    >>>     .. do op ..

    Is a syntactic sugar for this:

    >>> for i in range(3):
    >>>     try:
    >>>         .. do op ..
    >>>         break
    >>>     except RuntimeError:
    >>>         pass

    :param times: maximum times to retry this operation. By default (None) retry until the world ends.
    :param exc_classes: exception classes that should be considered failure. By default.
        catches everything (Exception).
    :param on_failure: callable to call when it fails times times. Callable will be called
        with a single argument, exception instance that was raised last. That exception will
        be swallowed, unless swallow_exception is set to False
    :param swallow_exception: the last exception will be swallowed, unless this is set to False
    :return: function result
    """
    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            if times is None:
                iterator = itertools.count()
            else:
                iterator = range(times)
            for _ in iterator:
                try:
                    return fun(*args, **kwargs)
                except exc_classes as e:
                    f = e
                    continue
            else:
                on_failure(f)
                if not swallow_exception:
                    raise f
        return inner
    return outer
