import concurrent.futures._base
import logging
import typing as tp
from concurrent.futures import Future as PythonFuture
from concurrent.futures._base import CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED

from satella.coding.typing import T

try:
    from concurrent.futures import InvalidStateError
except ImportError:
    class InvalidStateError(concurrent.futures._base.Error):
        """Raised when the future is in invalid state to execute given operation"""

LOGGER = logging.getLogger('concurrent.futures')
PRE_FINISHED = 'PRE-FINISHED'

concurrent.futures._base._STATE_TO_DESCRIPTION_MAP[PRE_FINISHED] = 'pre-finished'
concurrent.futures._base._FUTURE_STATES.append(PRE_FINISHED)


class Future(PythonFuture, tp.Generic[T]):
    """
    A future that allows it's callback handlers to change it's result before presenting
    it to the user.

    Use like this:

    >>> fut = Future()
    >>> fut.set_running_or_notify_cancel()
    >>> def transform_future(future):
    >>>     future.set_result(future.result() + 2)
    >>> fut.add_pre_done_callback(transform_future)
    >>> fut.set_result(2)
    >>> assert fut.result() == 4
    """

    def __init__(self):
        super().__init__()
        self._pre_done_callbacks = []
        self._done_callbacks = []

    def on_success(self, fun) -> 'Future':
        """
        Schedule function to be called with the result of this future as it's argument only if
        this future succeeds.

        :param fun: function to call
        :return: self
        """

        def inner(fut: PythonFuture):
            if fut._exception is not None:
                return
            return fun(fut._result)

        self.add_done_callback(inner)
        return self

    def on_failure(self, fun):
        """
        Schedule function to be called with the exception value that befall this future

        :param fun: function to call
        :return: self
        """

        def inner(fut: PythonFuture):
            if fut._exception is None:
                return
            return fun(fut._exception)

        self.add_done_callback(inner)
        return self

    def chain(self, fun) -> 'Future':
        """
        Schedule function to be called with the result of this future as it's argument (or
        exception value if the future excepted).

        :param fun: function to call
        :return: self
        """

        def inner(future):
            if future._exception is not None:
                result = future._exception
            else:
                result = future._result
            fun(result)

        self.add_done_callback(inner)
        return self

    def add_pre_done_callback(self, fn):
        """
        Attaches a callable that will be called just before the future finishes
        and can change the future's result (or insert an Exception).

        Args:
            fn: A callable that will be called with this future as its only
                argument just before the future completes or is cancelled.
        """
        with self._condition:
            if self._state not in [CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED]:
                self._pre_done_callbacks.append(fn)
                return
        # noinspection PyBroadException
        try:
            fn(self)
        except Exception:
            LOGGER.exception('exception calling callback for %r', self)

    def _invoke_pre_callbacks(self):
        for callback in self._pre_done_callbacks:
            # noinspection PyBroadException
            try:
                callback(self)
            except Exception:
                LOGGER.exception('exception calling callback for %r', self)

    def result(self, timeout=None) -> T:
        if self._state == PRE_FINISHED:
            return self.__get_result()
        else:
            return super().result(timeout)

    def exception(self, timeout: None) -> tp.Type[Exception]:
        if self._state == PRE_FINISHED:
            return self._exception
        else:
            return super().exception(timeout)

    def set_result(self, result: T) -> None:
        """Sets the return value of work associated with the future.

        Should only be used by Executor implementations and unit tests.
        """
        if self._state == PRE_FINISHED:
            self._result = result
        else:
            with self._condition:
                if self._state in {CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED}:
                    raise InvalidStateError('{}: {!r}'.format(self._state, self))
                self._result = result
                self._state = PRE_FINISHED
                self._invoke_pre_callbacks()
                self._state = FINISHED
                for waiter in self._waiters:
                    waiter.add_result(self)
                self._condition.notify_all()
            self._invoke_callbacks()

    def set_exception(self, exception):
        """Sets the result of the future as being the given exception.

        Should only be used by Executor implementations and unit tests.
        """
        if self._state == PRE_FINISHED:
            self._exception = exception
            self._result = None
        else:
            with self._condition:
                if self._state in {CANCELLED, CANCELLED_AND_NOTIFIED, FINISHED}:
                    raise InvalidStateError('{}: {!r}'.format(self._state, self))
                self._exception = exception
                self._state = PRE_FINISHED
                self._invoke_pre_callbacks()
                self._state = FINISHED
                for waiter in self._waiters:
                    waiter.add_exception(self)
                self._condition.notify_all()
            self._invoke_callbacks()


class WrappingFuture(Future):
    """
    A Satella future wrapping an existing Python future.

    Use like:

    >> wrapped = WrappingFuture(existing_python_future)
    """

    def __init__(self, source_future: PythonFuture):
        super().__init__()
        self.source_future = source_future
        self.source_future.add_done_callback(self._on_future_completed)
        self._old_state = source_future._state

    @property
    def _state(self):
        if self.source_future._state == FINISHED:
            return self._old_state
        else:
            return self.source_future._state

    @_state.setter
    def _state(self, v: str):
        self._old_state = v

    def set_running_or_notify_cancel(self) -> bool:
        return self.source_future.set_running_or_notify_cancel()

    def _on_future_completed(self, future: PythonFuture):
        if future._exception is not None:
            self.set_exception(future._exception)
        else:
            self.set_result(future._result)

    def cancel(self) -> bool:
        super().cancel()
        return self.source_future.cancel()


def wrap_if(fut: tp.Union[PythonFuture, Future]) -> Future:
    """
    Wrap a future, if it isn't already wrapped

    :param fut: either a Python Future or a Satella Future
    :return: a Satella future
    """
    if not isinstance(fut, Future):
        return WrappingFuture(fut)
    else:
        return fut
