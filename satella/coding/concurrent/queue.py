import typing as tp

import collections
import threading

from satella.coding.typing import T
from satella.exceptions import WouldWaitMore


class PeekableQueue(tp.Generic[T]):
    """
    A thread-safe FIFO queue that supports peek()ing for elements.
    """
    __slots__ = ('queue', 'lock')

    def __init__(self):
        super().__init__()
        self.queue = collections.deque()
        self.lock = threading.Lock()

    def put(self, item: T) -> None:
        """
        Add an element to the queue
        :param item:
        :return:
        """
        with self.lock:
            self.queue.append(item)

    def __acquire(self, timeout: tp.Optional[float]) -> None:
        if timeout is None:
            self.lock.acquire()
        else:
            if not self.lock.acquire(blocking=False, timeout=timeout):
                raise WouldWaitMore()

    def get(self, timeout: tp.Optional[float] = None) -> T:
        """
        Get an element.

        :param timeout: maximum amount of seconds to wait. Default value of None
            means wait as long as necessary
        :return: the item
        :raise WouldWaitMore: timeout has expired
        """
        self.__acquire(timeout)

        try:
            return self.queue.popleft()
        finally:
            self.lock.release()

    def peek(self, timeout: tp.Optional[float] = None) -> T:
        """
        Get an element without removing it from the top of the queue.

        :param timeout: maximum amount of seconds to wait. Default value of None
            means wait as long as necessary
        :return: the item
        :raise WouldWaitMore: timeout has expired
        """
        self.__acquire(timeout)

        try:
            return self.queue[0]
        finally:
            self.lock.release()

    def qsize(self) -> int:
        """
        Return the approximate size of the queue. Note, qsize() > 0 doesn’t
        guarantee that a subsequent get() will not block.
        :return: approximate size of the queue
        """
        return len(self.queue)

