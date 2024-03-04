import collections
import copy
import time
import typing as tp

from satella.coding.deleters import DictDeleter
from satella.coding.typing import T, NoArgCallable


class CancellableCallback:
    """
    A callback that you can cancel.

    Useful for event-driven software that looks through lists of callbacks and determines whether
    to delete them or further invalidate in some other way.

    If called, the function itself won't be called as well if this was cancelled. In this case
    a None will be returned instead of the result of callback_fun()

    This short circuits __bool__ to return not .cancelled.

    Hashable and __eq__-able by identity.

    :param callback_fun: function to call

    :ivar cancelled: whether this callback was cancelled (bool)
    """
    __slots__ = ('cancelled', 'callback_fun')

    def __bool__(self) -> bool:
        return not self.cancelled

    def __hash__(self) -> int:
        return hash(id(self))

    def __init__(self, callback_fun: tp.Callable):
        self.callback_fun = callback_fun
        self.cancelled = False

    def __call__(self, *args, **kwargs):
        if not self.cancelled:
            return self.callback_fun(*args, **kwargs)

    def cancel(self) -> None:
        """
        Cancel this callback.
        """
        self.cancelled = True


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
    __slots__ = ('callables', 'gather', 'swallow_exceptions',
                 '_has_cancellable_callbacks')

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
        self._has_cancellable_callbacks = False

    @property
    def has_cancelled_callbacks(self) -> bool:
        """
        Check whether this has any
        :class:`~satella.coding.concurrent.CancellableCallback` instances and whether any
        of them was cancelled
        """
        if not self._has_cancellable_callbacks:
            return False
        for clb in self.callables:
            if isinstance(clb, CancellableCallback) and not clb:
                return True
        return False

    def remove_cancelled(self) -> None:
        """
        Remove it's entries that are CancelledCallbacks and that were cancelled
        """
        if not self.has_cancelled_callbacks:
            return

        with DictDeleter(self.callables) as dd:
            for callable_ in dd:
                if isinstance(callable_, CancellableCallback) and not callable_:
                    dd.delete()

    def add(self, callable_: tp.Union[CancellableCallback, NoArgCallable[T]],
            one_shot: bool = False):
        """
        Add a callable.

        Can be a :class:`~satella.coding.concurrent.CancellableCallback`, in that case
        method :meth:`~satella.coding.concurrent.CallableGroup.remove_cancelled` might
        be useful.

        :param callable_: callable
        :param one_shot: if True, callable will be unregistered after single call
        """
        if isinstance(callable_, CancellableCallback):
            self._has_cancellable_callbacks = True
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

        As a side-effect, removes cancelled
        :class:`~satella.coding.concurrent.CancellableCallback` instances registered.

        :return: list of results if gather was set, else None
        """
        if self.has_cancelled_callbacks:
            self.remove_cancelled()

        callables = copy.copy(self.callables)
        self.callables.clear()

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

    Even if it's call is called more often than specified value, the callable just
    won't be called and None will be returned.

    :param interval: interval in seconds
    :param callable_: callable to call
    """
    __slots__ = ('interval', 'callable', 'last_called')

    def __init__(self, interval: float, callable_: tp.Callable):
        self.interval = interval  # type: float
        self.callable = callable_  # type: tp.Callable
        self.last_called = 0  # type: float

    def __call__(self, *args, **kwargs):
        if time.monotonic() - self.last_called >= self.interval:
            self.callable(*args, **kwargs)
            self.last_called = time.monotonic()
