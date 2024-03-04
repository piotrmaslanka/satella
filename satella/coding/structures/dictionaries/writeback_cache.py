import time
import typing as tp
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor

from satella.coding.concurrent.monitor import Monitor
from satella.coding.concurrent.sync import sync_threadpool
from satella.coding.recast_exceptions import silence_excs
from satella.coding.typing import V, K


class ExclusiveWritebackCache(tp.Generic[K, V]):
    """
    A dictionary implementing an exclusive write-back cache. By exclusive it is understood
    that only this object will be modifying the storage.

    :param write_method: a blocking callable (key, value) that writes the value to underlying
        storage.
    :param read_method: a blocking callable (key) -> value that retrieves the piece of data from
        the cache, or throws a KeyError to signal that the value does not exist
    :param delete_method: optional, a blocking callable (key) that erases the data from the storage.
        If not given, it will be a TypeError to delete the data from this storage
    :param executor: an executor to execute the calls with. If None (default) is given, a
        ThreadPoolExecutor with 4 workers will be created
    :param no_concurrent_executors: number of concurrent jobs that the executor is able
        to handle. This is used by sync()
    :param store_key_errors: whether to remember KeyErrors raised by read_method
    """
    __slots__ = ('executor', 'read_method', 'write_method', 'delete_method',
                 'no_concurrent_executors', 'in_cache', 'cache_lock',
                 'cache', 'operations', 'store_key_errors')

    def __init__(self, write_method: tp.Callable[[K, V], None],
                 read_method: tp.Callable[[K], V],
                 delete_method: tp.Optional[tp.Callable[[K], None]] = None,
                 executor: tp.Optional[Executor] = None,
                 no_concurrent_executors: tp.Optional[int] = None,
                 store_key_errors: bool = True
                 ):
        if executor is None:
            self.executor = ThreadPoolExecutor(max_workers=4)
        else:
            self.executor = executor
        self.store_key_errors = store_key_errors
        self.write_method = write_method
        self.delete_method = delete_method
        self.read_method = read_method
        self.no_concurrent_executors = no_concurrent_executors or 4
        self.in_cache = set()
        self.cache_lock = Monitor()
        self.cache = {}
        self.operations = 0

    def get_queue_length(self) -> int:
        """
        Return current amount of entries waiting for writeback
        """
        # noinspection PyProtectedMember
        if isinstance(self.executor, ThreadPoolExecutor):
            return self.executor._work_queue.qsize()
        elif isinstance(self.executor, ProcessPoolExecutor):
            return self.executor._call_queue.qsize()
        else:
            return 0

    def sync(self, timeout: tp.Optional[float] = None) -> None:
        """
        Wait until current tasks are complete.

        :param timeout: timeout to wait. None means wait indefinitely.
        :raises WouldWaitMore: if timeout has expired
        """
        while self.get_queue_length() > 0:
            time.sleep(0.1)

        def fix():
            return

        sync_threadpool(self.executor, max_wait=timeout)

    def _operate(self):
        self.operations += 1
        if self.operations > 100:
            with self.cache_lock:
                self.in_cache = set(self.cache.keys())
                self.operations = 0

    def __getitem__(self, item: K) -> V:
        self._operate()
        if item not in self.in_cache:
            try:
                value = self.executor.submit(self.read_method, item).result()
                with self.cache_lock:
                    self.in_cache.add(item)
                    self.cache[item] = value
                return value
            except KeyError:
                if self.store_key_errors:
                    with self.cache_lock:
                        self.in_cache.add(item)
                raise
        else:
            if item not in self.cache and self.store_key_errors:
                raise KeyError()
            else:
                return self.cache[item]

    def __delitem__(self, key: K) -> None:
        if self.delete_method is None:
            raise TypeError('Cannot delete from this writeback cache!')
        if self.store_key_errors:
            with self.cache_lock:
                self.in_cache.add(key)
        with silence_excs(KeyError):
            del self.cache[key]
        self.executor.submit(self.delete_method, key)
        self._operate()

    def __setitem__(self, key: K, value: V) -> None:
        with self.cache_lock:
            self.cache[key] = value
            self.in_cache.add(key)
        self.executor.submit(self.write_method, key, value)
        self._operate()
