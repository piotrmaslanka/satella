import collections
import copy
import time
import typing as tp

T = tp.TypeVar('T')


class CallableGroup(tp.Generic[T]):
    """
    This behaves like a function, but allows to add other functions to call
    when invoked, eg.

        c1 = Callable()

        c1.add(foo)
        c1.add(bar)

        c1(2, 3)

    Now both foo and bar will be called with arguments (2, 3). Their exceptions
    will be propagated.

    """
    __slots__ = ('callables', 'gather', 'swallow_exceptions')

    def __init__(self, gather: bool = True, swallow_exceptions: bool = False):
        """
        :param gather: if True, results from all callables will be gathered
                       into a list and returned from __call__
        :param swallow_exceptions: if True, exceptions from callables will be
                                   silently ignored. If gather is set,
                                   result will be the exception instance
        """
        self.callables = collections.OrderedDict()  # type: tp.Dict[tp.Callable, bool]
        self.gather = gather  # type: bool
        self.swallow_exceptions = swallow_exceptions  # type: bool

    def add(self, callable_: tp.Callable[[], T], one_shot: bool = False):
        """
        :param callable_: callable
        :param one_shot: if True, callable will be unregistered after single call
        """
        from ..structures.hashable_objects import HashableWrapper
        callable_ = HashableWrapper(callable_)
        if callable_ in self.callables:
            return
        self.callables[callable_] = one_shot

    def __call__(self, *args, **kwargs) -> tp.Optional[tp.List[T]]:
        """
        Run the callable. All registered callables will be called with
        passed arguments, so they should have the same arity.

        If callables raise, it will be passed through.

        :return: list of results if gather was set, else None
        """
        callables = copy.copy(self.callables)

        results = []

        for call, one_shot in callables.items():
            try:
                q = call(*args, **kwargs)
            except Exception as e:
                if not self.swallow_exceptions:
                    raise  # re-raise
                q = e

            if self.gather:
                results.append(q)

            if not one_shot:
                self.add(call, one_shot)

        if self.gather:
            return results


class CallNoOftenThan:
    """
    A class that will ensure that calls to given callable are made no more often
    than some interval.

    :param interval: interval in seconds
    :param callable_: callable to call
    """
    __slots__ = ('interval', 'callable', 'last_called')

    def __init__(self, interval: float, callable_: tp.Callable[[], None]):
        self.interval = interval  # type: float
        self.callable = callable_  # type: tp.Callable[[], None]
        self.last_called = 0  # type: float

    def __call__(self, *args, **kwargs):
        if time.monotonic() - self.last_called >= self.interval:
            self.callable(*args, **kwargs)
            self.last_called = time.monotonic()
