import queue
import typing as tp

from satella.coding.concurrent.monitor import Monitor
from satella.coding.recast_exceptions import silence_excs
from satella.coding.typing import T


class Subqueue(tp.Generic[T]):
    """
    Or a named queue is a collection of thread safe queues identified by name
    """

    def __init__(self):
        self.subqueues = {}  # type: tp.Dict[str, queue.Queue]
        self.subqueue_lock = Monitor()

    def assert_queue(self, queue_name: str) -> None:
        """
        Assure that we have a queue with a particular name in the dictionary
        """
        if queue_name not in self.subqueues:
            with self.subqueue_lock:
                if queue_name not in self.subqueues:  # double check for locking
                    self.subqueues[queue_name] = queue.Queue()

    def put(self, queue_name: str, obj: T) -> None:
        """
        Same semantics as queue.Queue.put
        """
        self.assert_queue(queue_name)
        self.subqueues[queue_name].put(obj)

    def get(self, queue_name: str, block=True, timeout=None) -> T:
        """
        Same semantics at queue.Queue.get
        """
        self.assert_queue(queue_name)
        return self.subqueues[queue_name].get(block, timeout)

    def qsize(self) -> int:
        """Calculate the total of entries"""
        return sum(que.qsize() for que in self.subqueues.values())

    def get_any(self) -> tp.Tuple[str, T]:
        """
        Return any message with name of the queue.

        This assumes block=False

        :return: a tuple of (queue_name, object)
        :raises: queue.Empty()
        """
        for queue_name, q in self.subqueues.items():
            with silence_excs(queue.Empty):
                return queue_name, q.get(block=False)
        else:
            raise queue.Empty('No messages in any of the queues')
