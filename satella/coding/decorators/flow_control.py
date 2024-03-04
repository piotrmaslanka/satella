import queue
import typing as tp

from satella.coding.decorators.decorators import wraps
from satella.coding.typing import ExceptionClassType, NoArgCallable, Predicate

Queue = tp.TypeVar('Queue')


def repeat_forever(fun):
    """
    A decorator that will place your function inside a while True loop.
    """

    @wraps(fun)
    def inner(*args, **kwargs):
        while True:
            fun(*args, **kwargs)

    doc = '' if inner.__doc__ is None else inner.__doc__
    inner.__doc__ = doc + "\nThis will be repeated forever."
    return inner


def queue_get(queue_getter: tp.Union[str, tp.Callable[[object], Queue]],
              timeout: tp.Optional[float] = None,
              exception_empty: tp.Union[
                  ExceptionClassType, tp.Tuple[ExceptionClassType, ...]] = queue.Empty,
              queue_get_method: tp.Callable[[Queue, tp.Optional[float]], tp.Any] =
              lambda x, timeout: x.get(
                  timeout=timeout),
              method_to_execute_on_empty: tp.Optional[tp.Union[str, tp.Callable]] = None):
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
    :param method_to_execute_on_empty: a callable, or a name of the method to be executed (with no
        arguments other than self) to execute in case queue.Empty was raised. Can be a callable -
        in that case it should expect no arguments, or can be a string, which will be assumed to be
        a method name

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
        def my_queue_getter(x):
            return getattr(x, queue_getter)
    else:
        my_queue_getter = queue_getter

    def outer(fun):
        @wraps(fun)
        def inner(self):
            try:
                que = my_queue_getter(self)
                item = queue_get_method(que, timeout)
                return fun(self, item)
            except exception_empty:
                if method_to_execute_on_empty is not None:
                    if callable(method_to_execute_on_empty):
                        method_to_execute_on_empty()
                    elif isinstance(method_to_execute_on_empty, str):
                        method = getattr(self, method_to_execute_on_empty)
                        method()

        return inner

    return outer


def loop_while(pred: tp.Union[Predicate, NoArgCallable[bool]] = lambda: True):
    """
    Decorator to loop the following function while predicate called on it's first argument is True.

    Use to mostly loop class methods basing off classes, like:

    >>> from satella.coding.predicates import x
    >>> class Terminable:
    >>>     terminated = False
    >>>     @loop_while(x.terminated == False)
    >>>     def run(self):
    >>>         ...

    You can also loop standard functions, like this:

    >>> a = {'terminating': False}
    >>> @loop_while(lambda: not a['terminating'])
    >>> def execute_while():
    >>>     ...

    :param pred: predicate to evaluate. Can accept either one element, in this case
        it will be fed the class instance, or accept no arguments, in which case
        it will be considered to annotate a method.

    Note that the function you decorate may only take arguments if it's a class method.
    If it's a standard method, then it should not take any arguments.
    """

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            pred_f = pred
            if len(args):
                def pred_f():
                    return pred(args[0])
            while pred_f():
                fun(*args, **kwargs)

        return inner

    return outer
