import time
import typing as tp

from satella.coding.concurrent.thread import Condition
from .measure import measure
from ..exceptions import WouldWaitMore


class ExponentialBackoff:
    """
    A class that will sleep increasingly longer on errors. Meant to be used in such a way:

    >>> eb = ExponentialBackoff(start=2, limit=30)
    >>> while not connect():
    >>>     eb.failed()
    >>>     eb.sleep()
    >>> eb.success()

    Also a structure that will mark an object (eg. the Internet access) as inaccessible for some
    duration. Usage is that case is like this:

    >>> eb = ExponentialBackoff(start=2, limit=30)
    >>> eb.failed()
    >>> self.assertFalse(eb.available)
    >>> time.sleep(2)
    >>> self.assertTrue(eb.available)

    Note that this structure is thread safe only when a single object is doing
    the :code:`success` or :code:`failed` calls, and other utilize
    :meth:`~satella.time.ExponentialBackoff.wait_until_available`.

    :param start: value at which to start
    :param limit: maximum sleep timeout
    :param sleep_fun: function used to sleep. Will accept a single argument - number of
        seconds to wait
    :param grace_amount: amount of fails() that this will survive before everything fails
    """
    __slots__ = 'start', 'limit', 'counter', 'sleep_fun', 'unavailable_until', 'condition', \
        'grace_amount', 'grace_counter'

    def __init__(self, start: float = 1, limit: float = 30,
                 sleep_fun: tp.Callable[[float], None] = time.sleep,
                 grace_amount: int = 0):
        self.start = start
        self.grace_amount = grace_amount
        self.grace_counter = 0
        self.limit = limit
        self.counter = 0
        self.sleep_fun = sleep_fun
        self.condition = Condition()
        self.unavailable_until = None

    def sleep(self) -> None:
        """
        Called when sleep is expected.
        """
        self.sleep_fun(self.counter)

    def failed(self) -> None:
        """
        Called when something fails.
        """
        if self.grace_amount == self.grace_counter:
            if self.counter == 0:
                self.counter = self.start
            else:
                self.counter = min(self.limit, self.counter * 2)
            self.unavailable_until = time.monotonic() + self.counter
        else:
            self.grace_counter += 1

    def wait_until_available(self, timeout: tp.Optional[float] = None) -> None:
        """
        Waits until the service is available

        :param timeout: maximum amount of seconds to wait. If waited more than that,
            WouldWaitMore will be raised
        :raises WouldWaitMore: waited for timeout and service still was not healthy
        """
        with measure(timeout=timeout) as m:
            while not m.timeouted:
                tn = self.time_until_next_check()
                if tn is None:
                    return
                self.condition.wait(timeout=tn, dont_raise=True)
            raise WouldWaitMore('timeouted while waiting for service to become healthy')

    def time_until_next_check(self) -> tp.Optional[float]:
        """Return the time until next health check, or None if the service is healthy"""
        if self.unavailable_until is None:
            return None
        else:
            t = time.monotonic()
            if t > self.unavailable_until:
                self.unavailable_until = None
                return None
            else:
                return self.unavailable_until - t

    @property
    def ready_for_next_check(self) -> bool:
        """
        :return: Has  :meth:`~satella.time.ExponentialBackoff.failure` been called only
            in the last waiting period?
        """
        if self.unavailable_until is None:
            return True
        elif time.monotonic() > self.unavailable_until:
            self.unavailable_until = None
            return True
        else:
            return False

    @property
    def available(self) -> bool:
        """Was the status of the last call :code:`success`?"""
        return self.counter == 0

    def success(self) -> None:
        """
        Called when something successes.
        """
        self.counter = 0
        self.grace_counter = 0
        self.unavailable_until = None
        self.condition.notify_all()
