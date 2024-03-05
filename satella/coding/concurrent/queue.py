import collections
import threading
import typing as tp

from satella.coding.concurrent.thread import Condition
from satella.coding.recast_exceptions import rethrow_as
from satella.coding.typing import T
from satella.exceptions import WouldWaitMore, Empty
from satella.time.measure import measure


class PeekableQueue(tp.Generic[T]):
    """
    A thread-safe FIFO queue that supports peek()ing for elements.
    """
    __slots__ = ('queue', 'lock', 'inserted_condition')

    def __init__(self):
        super().__init__()
        self.queue = collections.deque()
        self.lock = threading.Lock()
        self.inserted_condition = Condition()

    def put(self, item: T) -> None:
        """
        Add an element to the queue

        :param item: element to add
        """
        with self.lock:
            self.queue.append(item)
        self.inserted_condition.notify()

    def put_many(self, items: tp.Sequence[T]) -> None:
        """
        Put multiple items

        :param items: sequence of items to put
        """
        with self.lock:
            items_count = 0
            for item in items:
                items_count += 1
                self.queue.append(item)
        self.inserted_condition.notify(items_count)

    def __get_timeout_none(self, item_getter):
        while True:
            self.lock.release()
            self.inserted_condition.wait()
            self.lock.acquire()
            if len(self.queue):
                try:
                    return item_getter(self.queue)
                finally:
                    self.lock.release()

    def __get_timeout(self, item_getter, timeout):
        with measure(timeout=timeout) as measurement:
            while not measurement.timeouted:
                self.lock.release()
                # raises WouldWaitMore
                self.inserted_condition.wait(timeout=measurement.time_remaining)
                self.lock.acquire()
                if len(self.queue):
                    try:
                        return item_getter(self.queue)
                    finally:
                        self.lock.release()
            else:
                self.lock.release()
                raise Empty('queue is empty')

    @rethrow_as(WouldWaitMore, Empty)
    def __get(self, timeout, item_getter) -> T:
        self.lock.acquire()
        if len(self.queue):
            # Fast path
            try:
                return item_getter(self.queue)
            finally:
                self.lock.release()
        else:
            if timeout is None:
                return self.__get_timeout_none(item_getter)
            else:
                return self.__get_timeout(item_getter, timeout)

    def get(self, timeout: tp.Optional[float] = None) -> T:
        """
        Get an element.

        :param timeout: maximum amount of seconds to wait. Default value of None
            means wait as long as necessary
        :return: the item
        :raise Empty: queue was empty
        """
        return self.__get(timeout, lambda queue: queue.popleft())

    def peek(self, timeout: tp.Optional[float] = None) -> T:
        """
        Get an element without removing it from the top of the queue.

        :param timeout: maximum amount of seconds to wait. Default value of None
            means wait as long as necessary
        :return: the item
        :raise WouldWaitMore: timeout has expired
        """
        return self.__get(timeout, lambda queue: queue[0])

    def qsize(self) -> int:
        """
        Return the approximate size of the queue. Note, qsize() > 0 doesn’t
        guarantee that a subsequent get() will not block.
        :return: approximate size of the queue
        """
        return len(self.queue)
