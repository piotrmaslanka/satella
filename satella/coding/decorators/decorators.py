import inspect
import time
import typing as tp
import warnings

from satella.coding.typing import T, U
from satella.exceptions import PreconditionError

Expression = tp.NewType('Expression', str)


# noinspection PyPep8Naming
def _TRUE(x):
    return True


# taken from https://stackoverflow.com/questions/1288498/using-the-same-decorator-with-arguments-wi\
# th-functions-and-methods
def chain_functions(fun_first: tp.Callable[..., tp.Union[tp.Tuple[tp.Tuple, tp.Dict],
                                                         tp.Dict, tp.Tuple]]) -> tp.Callable:
    """
    A decorator to chain function calls.
    This function is expected to return:

     * a 2-tuple [tp.Tuple, tp.Dict] - args and kwargs for the next function
     * tp.Dict - only kwargs will be passed
     * any other tuple - only args will be passed
     * any other type - will be passed as a first argument

    of arguments to pass to wrapped function. So this

    >>> def test3(...):
    >>>     ...
    >>> def test2(...):
    >>>     ...
    >>> def test(...):
    >>>     args, kwargs = test2(...)
    >>>     return test(3)
    >>> v = test(a, b, c)

    Is equivalent to this:
    >>> @chain_functions
    >>> def test2(...):
    >>>     ...
    >>> @test2
    >>> def test3(...):
    >>>     ...
    >>> v = test3(a, b, c)
    """

    def outer(fun_next):
        @wraps(fun_next)
        def inner(*args, **kwargs):
            ret = fun_first(*args, **kwargs)
            if isinstance(ret, dict):
                args = ()
                kwargs = ret
            elif isinstance(ret, tuple) and len(ret) == 2:
                args, kwargs = ret
            elif isinstance(ret, tuple):
                args = ret
                kwargs = {}
            else:
                args = ret,
                kwargs = {}
            return fun_next(*args, **kwargs)

        return inner

    return outer


def default_return(v: tp.Any):
    """
    Makes the decorated function return v instead of None, if it would return None.
    If it would return something else, that else is returned.

    Eg:

    >>> @default_return(5)
    >>> def return(v):
    >>>     return v
    >>> assert return(None) == 5
    >>> assert return(2) == 2

    :param v: value to return if calling the function would return None
    """

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            v_a = fun(*args, **kwargs)
            if v_a is None:
                return v
            else:
                return v_a

        return inner

    return outer


def return_as_list(ignore_nulls: bool = False):
    """
    Enables you to write a list-returning functions using a decorator. Example:

    >>> def make_a_list(lst):
    >>>     output = []
    >>>     for item in lst:
    >>>         output.append(item)
    >>>     return output

    Is equivalent to:

    >>> @return_as_list()
    >>> def make_a_list(lst):
    >>>     for item in lst:
    >>>         yield item

    Essentially a syntactic sugar for @for_argument(returns=list)

    :param ignore_nulls: if True, then if your function yields None, it won't be appended.
    """

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            output = []
            for item in fun(*args, **kwargs):
                if item is None and ignore_nulls:
                    continue
                output.append(item)
            return output

        return inner

    return outer


def cache_memoize(cache_duration: float, time_getter: tp.Callable[[], float] = time.monotonic):
    """
    A thread-safe memoizer that memoizes the return value for at most cache_duration seconds.

    :param cache_duration: cache validity, in seconds
    :param time_getter: a callable without arguments that yields us a time marker

    Usage example:

    >>> @cache_memoize(10)
    >>> def expensive_but_idempotent_operation(a):
    >>>     ...

    >>> a = expensive_but_idempotent_operation(2)
    >>> b = expensive_but_idempotent_operation(2)   # is much faster than computing the value anew
    >>> time.sleep(10)
    >>> c = expensive_but_idempotent_operation(2)   # function body is computed anew
    """
    from satella.coding.concurrent import MonitorDict, Monitor

    def outer(fun):
        fun.memoize_timestamps = MonitorDict()
        fun.memoize_values = {}

        @wraps(fun)
        def inner(*args, **kwargs):

            now = time_getter()

            with Monitor.acquire(fun.memoize_timestamps):
                if args in fun.memoize_timestamps:
                    ts = fun.memoize_timestamps[args]
                    if now - ts > cache_duration:
                        with Monitor.release(fun.memoize_timestamps):
                            v = fun(*args, **kwargs)
                        fun.memoize_timestamps[args] = now
                        fun.memoize_values[args] = v
                else:
                    with Monitor.release(fun.memoize_timestamps):
                        v = fun(*args, **kwargs)
                    fun.memoize_timestamps[args] = now
                    fun.memoize_values[args] = v

                return fun.memoize_values[args]

        return inner

    return outer


def memoize(fun):
    """
    A thread safe memoizer based on function's ONLY positional arguments.

    Note that this will make your function execute it at most one thread, the
    remaining ones will have to wait.

    Usage example:

    >>> @memoize
    >>> def expensive_but_idempotent_operation(a):
    >>>     ...

    >>> a = expensive_but_idempotent_operation(2)
    >>> b = expensive_but_idempotent_operation(2)   # is much faster than computing the value anew
    """
    from satella.coding.concurrent.monitor import MonitorDict, Monitor

    fun.memoizer = MonitorDict()

    @wraps(fun)
    def inner(*args, **kwargs):
        with Monitor.acquire(fun.memoizer):
            if args in fun.memoizer:
                return fun.memoizer[args]
            else:
                with Monitor.release(fun.memoizer):
                    v = fun(*args, **kwargs)
                fun.memoizer[args] = v
                return v

    return inner


def wraps(cls_to_wrap: tp.Type) -> tp.Callable[[tp.Type], tp.Type]:
    """
    A functools.wraps() but for classes.

    As a matter of fact, this can replace functools.wraps() entirely.
    This replaces __doc__, __name__, __module__ and __annotations__.
    It also sets a correct __wrapped__.

    :param cls_to_wrap: class to wrap
    """

    def outer(cls: tp.Type) -> tp.Type:
        if hasattr(cls_to_wrap, '__doc__'):
            try:
                cls.__doc__ = cls_to_wrap.__doc__
            except AttributeError:
                pass
        if hasattr(cls_to_wrap, '__name__'):
            try:
                cls.__name__ = cls_to_wrap.__name__
            except (AttributeError, TypeError):
                pass
        if hasattr(cls_to_wrap, '__module__'):
            try:
                cls.__module__ = cls_to_wrap.__module__
            except AttributeError:
                pass
        if hasattr(cls_to_wrap, '__annotations__'):
            try:
                cls.__annotations__ = cls_to_wrap.__annotations__
            except (AttributeError, TypeError):
                pass
        try:
            sig = inspect.signature(cls_to_wrap)
            cls.__signature__ = sig
        except (TypeError, ValueError, RecursionError, AttributeError):
            pass
        try:
            cls.__wrapped__ = cls_to_wrap
        except AttributeError:
            pass
        return cls

    return outer


def has_keys(keys: tp.List[str]):
    """
    A decorator for asserting that a dictionary has given keys. Will raise PreconditionError if
    it doesn't.

    This outputs a callable that accepts a dict and returns True if it has all the keys
    necessary.

    Returns True if the dict has all necessary keys.

    This is meant to be used in conjunction with @precondition

    .. deprecated:: 2.14.22

    :param keys: list of keys to expect
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0. '
                  'Use satella.coding.predicates.has_keys instead', DeprecationWarning)

    def inner(dictionary: dict) -> bool:
        for key in keys:
            if key not in dictionary:
                raise PreconditionError('Key %s not found in dict' % (key,))
        return True

    return inner


def short_none(clb: tp.Union[Expression, tp.Callable[[T], U]]) -> tp.Callable[
    [tp.Optional[T]], tp.Optional[U]]:
    """
    Accept a callable. Return a callable that executes it only if passed a no-None arg,
    and returns its result. If passed a None, return a None

    callable can also be a string, in this case it will be appended to lambda x: and eval'd

    :param clb: callable/1->1
    :return: a modified callable
    """
    if isinstance(clb, str):
        q = dict(globals())
        exec('_callable = lambda x: ' + clb, q)
        clb = q['_callable']

    @wraps(clb)
    def inner(arg: tp.Optional[T]) -> tp.Optional[U]:
        if arg is None:
            return None
        else:
            return clb(arg)

    return inner


def call_method_on_exception(exc_classes, method_name, *args, **kwargs):
    """
    A decorator for instance methods to call provided method with given arguments
    if given call fails.

    Example use:

    >>> class Test:
    >>>     def close(self):
    >>>         ...
    >>>     @call_method_on_exception(ValueError, 'close')
    >>>     def read(self, bytes):
    >>>         raise ValueError()

    Exception class determination is done by isinstance, so you can go wild with metaclassing.
    Exception will be swallowed. The return value will be taken from the called function.

    Note that the called method must be an instance method.

    :param exc_classes: a tuple or an instance class to which react
    :param method_name: name of the method. It must be gettable by getattr
    :param args: arguments to pass to given method
    :param kwargs: keyword arguments to pass to given method
    """
    def outer(fun):
        @wraps(fun)
        def inner(self, *f_args, **f_kwargs):
            try:
                return fun(self, *f_args, **f_kwargs)
            except Exception as e:
                if isinstance(e, exc_classes):
                    return getattr(self, method_name)(*args, **kwargs)
                else:
                    raise
        return inner
    return outer

