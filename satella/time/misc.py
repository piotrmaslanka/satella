import time
import typing as tp

__all__ = ['time_as_int', 'time_ms', 'sleep', 'time_us', 'ExponentialBackoff']

from satella.coding.concurrent.thread import Condition
from satella.exceptions import WouldWaitMore
from .parse import parse_time_string
from .measure import measure


def sleep(y: tp.Union[str, float], abort_on_interrupt: bool = False) -> bool:
    """
    Sleep for given interval.

    This won't be interrupted by KeyboardInterrupted, and always will sleep for given time interval.
    This will return at once if x is negative

    :param y: the interval to wait in seconds, can be also a time string
    :param abort_on_interrupt: whether to abort at once when KeyboardInterrupt is seen
    :returns: whether the function has completed its sleep naturally. False is seen on
        aborts thanks to KeyboardInterrupt only if abort_on_interrupt is True
    """
    y = parse_time_string(y)
    if y < 0:
        return

    with measure() as measurement:
        while measurement() < y:
            try:
                time.sleep(y - measurement())
            except KeyboardInterrupt:
                if abort_on_interrupt:
                    return False
    return True


def time_as_int() -> int:
    """
    Syntactic sugar for

    >>> from time import time
    >>> int(time())
    """
    return int(time.time())


def time_ms() -> int:
    """
    Syntactic sugar for

    >>> from time import time
    >>> int(time()*1000)

    This will try to use time.time_ns() if available
    """
    try:
        return time.time_ns() // 1000000
    except AttributeError:
        return int(time.time() * 1000)


def time_us() -> int:
    """
    Syntactic sugar for

    >>> from time import time
    >>> int(time()*1000000)

    This will try to use time.time_ns() if available
    """
    try:
        return time.time_ns() // 1000
    except AttributeError:
        return int(time.time() * 1000000)



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
    """
    __slots__ = 'start', 'limit', 'counter', 'sleep_fun', 'unavailable_until', 'condition'

    def __init__(self, start: float = 1, limit: float = 30,
                 sleep_fun: tp.Callable[[float], None] = sleep):
        self.start = start
        self.limit = limit
        self.counter = start
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
        if self.counter == 0:
            self.counter = self.start
        else:
            self.counter = min(self.limit, self.counter * 2)
        self.unavailable_until = time.monotonic() + self.counter

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
        self.unavailable_until = None
        self.condition.notify_all()
