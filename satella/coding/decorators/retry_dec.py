import itertools
import typing as tp

from satella.coding.decorators.decorators import wraps
from satella.coding.typing import ExceptionClassType


def retry(times: tp.Optional[int] = None,
          exc_classes: tp.Union[ExceptionClassType, tp.Tuple[ExceptionClassType, ...]] = Exception,
          on_failure: tp.Callable[[Exception], None] = lambda e: None,
          swallow_exception: bool = True,
          call_on_failure: tp.Optional[tp.Callable[[Exception], None]] = None,
          call_on_success: tp.Optional[tp.Callable[[int], None]] = None,
          call_between_retries: tp.Optional[tp.Callable[[Exception], None]] = None):
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
    :param call_on_failure: a callable that will be called upon failing to do this, with an
        exception as it's sole argument. It's result will be discarded.
    :param call_on_success: a callable that will be called with a single argument: the number
        of retries that it took to finish the job. It's result will be discarded.
    :param call_between_retries: called between retries with a single argument, the Exception
        instance that forced the retry.
    :return: function result
    """
    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            if times is None:
                iterator = itertools.count()
            else:
                iterator = range(times)
            for i in iterator:
                try:
                    y = fun(*args, **kwargs)
                    if call_on_success is not None:
                        call_on_success(i)
                    return y
                except exc_classes as e:
                    f = e
                    if call_between_retries is not None:
                        call_between_retries(e)
                    continue
            else:
                on_failure(f)
                if call_on_failure is not None:
                    call_on_failure(f)
                if not swallow_exception:
                    raise f
        return inner
    return outer
