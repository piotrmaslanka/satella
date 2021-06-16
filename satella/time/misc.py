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


