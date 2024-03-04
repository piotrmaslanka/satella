import time
import typing as tp
from threading import Event

from satella.coding.misc import _BLANK
from satella.coding.typing import T
from satella.exceptions import WouldWaitMore


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
        self.val = _BLANK

    def set_value(self, va: T) -> None:
        """
        Set a value and wake up all the threads waiting on it.

        :param va: value to set
        :raises ValueError: value is already set
        """
        if self.val is not _BLANK:
            raise ValueError('Value curently set!')
        self.val = va
        self.lock.set()

    def result(self, timeout=None) -> T:
        """An alias for :meth:`~satella.coding.concurrent.DeferredValue.value`"""
        return self.value(timeout)

    def value(self, timeout: tp.Optional[float] = None) -> T:
        """
        Wait until value is available, and return it.

        :param timeout: number of seconds to wait. If None is given, this will take as long as necessary.
        :return: a value
        :raises WouldWaitMore: timeout was given and it has expired
        """
        if self.val is not _BLANK:
            return self.val
        tout = self.lock.wait(timeout)
        if not tout:
            raise WouldWaitMore()
        return self.val
