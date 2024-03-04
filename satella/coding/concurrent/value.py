import time
import typing as tp
from threading import Event

from satella.coding.typing import T
from satella.exceptions import WouldWaitMore


class _UNSET:
    pass


class DeferredValue(tp.Generic[T]):
    """
    A class that allows you to pass arguments that will be available later during runtime.

    Usage:

    >>> def thread1(value):
     >>>     print(value.value())

    >>> val = DeferredValue()
    >>> threading.Thread(target=thread1, args=(val, )).start()
    >>> time.sleep(10)
    >>> val.set_value(3)
    """

    __slots__ = 'val', 'lock'

    def __init__(self):
        self.lock = Event()
        self.val = _UNSET

    def set_value(self, va: T) -> None:
        """
        Set a value and wake up all the threads waiting on it.

        :param va: value to set
        :raises ValueError: value is already set
        """
        if self.val is not _UNSET:
            raise ValueError('Value curently set!')
        self.val = va
        self.lock.set()

    def value(self, timeout: tp.Optional[float] = None) -> T:
        """
        Wait until value is available.

        :return: a value
        :raises WouldWaitMore: timeout was given and it has expired
        """
        if self.val is not _UNSET:
            return self.val
        tout = self.lock.wait(timeout)
        if not tout:
            raise WouldWaitMore()
        return self.val
