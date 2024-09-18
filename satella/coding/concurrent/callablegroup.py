from __future__ import annotations
import collections
import copy
import time
import typing as tp

from satella.coding.deleters import DictDeleter, IterMode
from satella.coding.typing import T, NoArgCallable
import inspect


class CancellableCallback:
    """
    A callback that you can cancel.

    Useful for event-driven software that looks through lists of callbacks and determines whether
    to delete them or further invalidate in some other way.

    If called, the function itself won't be called as well if this was cancelled. In this case
    a None will be returned instead of the result of callback_fun()

    This short circuits __bool__ to return not .cancelled. So, the bool value of this callback depends on whether it
    has been cancelled or not.

    Hashable and __eq__-able by identity. Equal only to itself.

    :param callback_fun: function to call
    :param hash: reserved for internal use, don't use

    :ivar cancelled: whether this callback was cancelled (bool)
    :ivar one_shotted: whether this callback was invoked (bool)
    """
    __slots__ = 'cancelled', 'callback_fun', 'one_shotted'

    def __bool__(self) -> bool:
        return not self.cancelled

    def __init__(self, callback_fun: tp.Callable):
        self.callback_fun = callback_fun
        self.cancelled = False
        self.one_shotted = False

    def __hash__(self):
        return hash(id(self)) ^ self.__hash

    def __eq__(self, other: CancellableCallback) -> bool:
        return id(self) == id(other) and self.cancelled == other.cancelled

    def __call__(self, *args, **kwargs):
        if not self.cancelled:
            return self.callback_fun(*args, **kwargs)

    def cancel(self) -> None:
        """
        Cancel this callback.
        """
        self.cancelled = True


def _callable_to_cancellablecallback(callback: NoArgCallable) -> CancellableCallback:
    if isinstance(callback, CancellableCallback):
        return callback
    if callable(callback):
        return CancellableCallback(callback)
    raise ValueError('Invalid callable')


class CancellableCallbackGroup:
    """

    A group of callbacks that you can simultaneously cancel.

    Immutable. Also, hashable and __eq__able.

    Regarding it's truth value - it's True if at least one callback has not been cancelled.
    """

    def __init__(self, callbacks: tp.Iterable[CancellableCallback]):
        self.callbacks = list(callbacks)  # type: tp.List[CancellableCallback]

    def cancel(self) -> None:
        """
        Cancel all of the callbacks.
        """
        for callback in self.callbacks:
            callback.cancel()

    def __bool__(self) -> bool:
        return any(not callback.cancelled for callback in self.callbacks)

    def __hash__(self):
        y = 0
        for callback in self.callbacks:
            y ^= hash(callback)
        return y


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
    __slots__ = 'callables', 'gather', 'swallow_exceptions',

    def __init__(self, gather: bool = True, swallow_exceptions: bool = False):
        self.callables = collections.OrderedDict()  # type: tp.Dict[CancellableCallback, bool]
        self.gather = gather  # type: bool
        self.swallow_exceptions = swallow_exceptions  # type: bool

    @property
    def has_cancelled_callbacks(self) -> bool:
        """
        Check whether this has any
        :class:`~satella.coding.concurrent.CancellableCallback` instances and whether any
        of them was cancelled
        """
        for clb in self.callables:
            if clb:
                return True
        return False

    def remove_cancelled(self) -> None:
        """
        Remove it's entries that are CancelledCallbacks and that were cancelled and move one shots
        """
        with DictDeleter(self.callables, iter_mode=IterMode.ITER_ITEMS) as dd:
            for callable_, oneshot in dd:
                if isinstance(callable_, CancellableCallback) and not callable_.cancelled:
                    dd.delete()
                if oneshot:
                    dd.delete()

    def add_many(self, callable_: tp.Sequence[tp.Union[NoArgCallable,
                 tp.Tuple[NoArgCallable, bool]]]) -> CancellableCallbackGroup:
        """
        Add multiple callbacks

        Basically every callback is cancellable.

        .. warning: Same callable cannot be added twice. A RuntimeError will be raised in that case.

        :param callable_: sequence of either callables with will be registered as multiple-shots or a tuple of callback
            (with an argument to register it as a one-shot)
        :returns: CancellableCallbackGroup to cancel all of the callbacks
        """

        cancellable_callbacks = []
        for clbl in callable_:
            if isinstance(clbl, tuple):
                clbl_, one_shot = clbl
                canc_callback = _callable_to_cancellablecallback(clbl_)
            else:
                one_shot = False
            cancellable_callbacks.append(canc_callback)
            self.add(canc_callback, one_shot=one_shot)
            return CancellableCallbackGroup(cancellable_callbacks)

    def add(self, callable_: tp.Union[CancellableCallback, NoArgCallable[T]],
            one_shot: bool = False) -> CancellableCallback:
        """
        Add a callable.

        Can be a :class:`~satella.coding.concurrent.CancellableCallback`, in that case
        method :meth:`~satella.coding.concurrent.CallableGroup.remove_cancelled` might
        be useful.

        .. warning: Same callable cannot be added twice. A RuntimeError will be raised in that case.

        Basically every callback is cancellable.

        :param callable_: callable
        :param one_shot: if True, callable will be unregistered after single call
        :param hash: internal, don't use
        :returns: callable_ if it was a cancellable callback, else one constructed after it

        .. deprecated:: v2.25.5
            Do not pass a CancellableCallback, you'll get your own
        """
        if not isinstance(callable_, CancellableCallback):
            callable_ = _callable_to_cancellablecallback(callable_)
            self.callables[callable_] = one_shot
        if callable_ in self.callables:
            raise RuntimeError('Same callable added twice')
        return callable_

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
            else:
                call.one_shotted = True

        if self.gather:
            return results

    def __len__(self):
        self.remove_cancelled()
        return len(self.callables)


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
