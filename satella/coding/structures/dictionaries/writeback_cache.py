import time
import typing as tp
from concurrent.futures import Executor, ThreadPoolExecutor, wait, ProcessPoolExecutor

from satella.coding.recast_exceptions import silence_excs

K = tp.TypeVar('K')
V = tp.TypeVar('V')


class ExclusiveWritebackCache(tp.Generic[K, V]):
    """
    A dictionary implementing an exclusive write-back cache. By exclusive it is understood
    that only this object will be modifying the storage.

    :param write_method: a blocking callable (key, value) that writes the value to underlying storage.
    :param read_method: a blocking callable (key) -> value that retrieves the piece of data from the cache,
        or throws a KeyError to signal that the value does not exist
    :param delete_method: optional, a blocking callable (key) that erases the data from the storage.
        If not given, it will be a TypeError to delete the data from this storage
    :param executor: an executor to execute the calls with. If None (default) is given, a
        ThreadPoolExecutor with 4 workers will be created
    :param no_concurrent_executors: number of concurrent jobs that the executor is able
        to handle. This is used by sync()
    """
    def __init__(self, write_method: tp.Callable[[K, V], None],
                 read_method: tp.Callable[[K], V],
                 delete_method: tp.Optional[tp.Callable[[K], None]] = None,
                 executor: tp.Optional[Executor] = None,
                 no_concurrent_executors: tp.Optional[int] = None
                 ):
        if executor is None:
            self.executor = ThreadPoolExecutor(max_workers=4)
        else:
            self.executor = executor
        self.write_method = write_method
        self.delete_method = delete_method
        self.read_method = read_method
        self.no_concurrent_executors = no_concurrent_executors or 4
        self.in_cache = set()
        self.cache = {}

        if isinstance(self.executor, ThreadPoolExecutor):
            def get_queue_length():
                # noinspection PyProtectedMember
                return self.executor._work_queue.qsize()
        elif isinstance(self.executor, ProcessPoolExecutor):
            def get_queue_length():
                # noinspection PyProtectedMember
                return self.executor._call_queue.qsize()
        else:
            def get_queue_length():
                return 0
        self._get_queue_length = get_queue_length

    def sync(self):
        """
        Wait until current tasks are complete.

        Note that this guarantees nothing, and is best-effort only
        """
        while self._get_queue_length() > 0:
            time.sleep(0.1)

        def fix():
            return

        futures = [self.executor.submit(fix) for _ in range(self.no_concurrent_executors)]
        wait(futures)

    def __getitem__(self, item: K) -> V:
        if item not in self.in_cache:
            try:
                value = self.executor.submit(self.read_method, item).result()
                self.in_cache.add(item)
                self.cache[item] = value
                return value
            except KeyError:
                self.in_cache.add(item)
                raise
        else:
            if item not in self.cache:
                raise KeyError()
            else:
                return self.cache[item]

    def __delitem__(self, key: K) -> None:
        if self.delete_method is None:
            raise TypeError('Cannot delete from this writeback cache!')
        self.in_cache.add(key)
        with silence_excs(KeyError):
            del self.cache[key]
        self.executor.submit(self.delete_method, key)

    def __setitem__(self, key: K, value: V) -> None:
        self.cache[key] = value
        self.in_cache.add(key)
        self.executor.submit(self.write_method, key, value)

