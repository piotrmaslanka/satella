import queue
import typing as tp

from satella.exceptions import PreconditionError

T = tp.TypeVar('T')
U = tp.TypeVar('U')
Expression = tp.NewType('Expression', str)


# noinspection PyPep8Naming
def _TRUE(x):
    return True


Queue = tp.TypeVar('Queue')


def queue_get(queue_getter: tp.Callable[[object], Queue], timeout: tp.Optional[float] = None,
              exception_empty=queue.Empty,
              queue_get_method: tp.Callable[[Queue, tp.Optional[float]], tp.Any] =
              lambda x, timeout: x.get(
                  timeout=timeout)):
    """
    A decorator for class methods that consume from a queue.

    Timeout of None means block forever.

    First attribute of the decorator-given function must be a normal instance method
    accepting an element taken from the queue, so it must accepts two arguments - first is
    self, second is the element from the queue.

    :param queue_getter: a callable that will render us the queue, or a string, which will be
        translated to a property name
    :param timeout: a timeout to wait. If timeout happens, simple no-op will be done and None
        will be returned.
    :param exception_empty: exception (or a tuple of exceptions) that are raised on queue being
        empty.
    :param queue_get_method: a method to invoke on this queue. Accepts two arguments - the first
        is the queue, the second is the timeout. It has to follow the type signature given.

    Use instead of:

    >>> class QueueProcessor:
    >>>     def __init__(self, queue):
    >>>         self.queue = queue
    >>>     def do(self):
    >>>         try:
    >>>             msg = self.queue.get(timeout=TIMEOUT)
    >>>         except queue.Empty:
    >>>             return

    Instead of aforementioned code, please use:

    >>> class QueueProcessor:
    >>>     def __init__(self, queue):
    >>>         self.queue = queue
    >>>     @queue_get(lambda self: self.queue, timeout=TIMEOUT)
    >>>     def do(self, msg):
    >>>         ...
    """
    if isinstance(queue_getter, str):
        my_queue_getter = lambda x: getattr(x, queue_getter)
    else:
        my_queue_getter = queue_getter

    def outer(fun):
        @wraps(fun)
        def inner(self):
            try:
                que = my_queue_getter(self)
                item = queue_get_method(que, timeout)
            except exception_empty:
                return
            return fun(self, item)

        return inner

    return outer


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


def wraps(cls_to_wrap: tp.Type) -> tp.Callable[[tp.Type], tp.Type]:
    """
    A functools.wraps() but for classes.

    As a matter of fact, this can replace functools.wraps() entirely.

    :param cls_to_wrap: class to wrap
    """

    def outer(cls: tp.Type) -> tp.Type:
        if hasattr(cls_to_wrap, '__doc__'):
            cls.__doc__ = cls_to_wrap.__doc__
        if hasattr(cls_to_wrap, '__name__'):
            cls.__name__ = cls_to_wrap.__name__
        if hasattr(cls_to_wrap, '__module__'):
            cls.__module__ = cls_to_wrap.__module__
        if hasattr(cls_to_wrap, '__annotations__'):
            cls.__annotations__ = cls_to_wrap.__annotations__
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

    :param keys: list of keys to expect
    """

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
