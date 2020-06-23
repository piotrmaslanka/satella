import time
import typing as tp
from concurrent.futures import ThreadPoolExecutor, Executor, Future

from satella.coding.recast_exceptions import silence_excs

K, V = tp.TypeVar('K'), tp.TypeVar('V')


class CacheDict(tp.Mapping[K, V]):
    """
    A dictionary that you can use as a cache.

    The idea is that you might want to cache some values, and they might be stale
    after some interval (after which they will need to be refreshed), and they will
    expire after some other interval (after which a call to get them will block
    until they are refreshed), but stale values are safe to serve from memory, while
    expired values are not and the dict will need to block until they are available.

    If a stale value is read, a refresh is scheduled in the background for it.
    If an expired value is read, it will block until the result is available.
    Else, the value is served straight from fast memory.

    Note that value_getter raising KeyError is not cached, so don't use this
    cache for situations where misses are frequent.

    :param stale_interval: time in seconds after which an entry will be stale, ie.
        it will be served from cache, but a task will be launched in background to
        refresh it
    :param expiration_interval: time in seconds after which an entry will be ejected
        from dict, and further calls to get it will block until the entry is available
    :param value_getter: a callable that accepts a key, and returns a value for given entry.
        If value_getter raises KeyError, then given entry will be evicted from the cache
    :param value_getter_executor: an executor to execute the value_getter function in background.
        If None is passed, a ThreadPoolExecutor will be used with max_workers of 4.
    """

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __init__(self, stale_interval: float, expiration_interval: float,
                 value_getter: tp.Callable[[K], V],
                 value_getter_executor: tp.Optional[Executor] = None):
        assert stale_interval <= expiration_interval, 'Stale interval may not be larger than expiration interval!'
        self.stale_interval = stale_interval
        self.expiration_interval = expiration_interval
        self.value_getter = value_getter
        if value_getter_executor is None:
            value_getter_executor = ThreadPoolExecutor(max_workers=4)
        self.value_getter_executor = value_getter_executor
        self.data = {}              # type: tp.Dict[K, V]
        self.timestamp_data = {}    # type: tp.Dict[K, float]
        self.missed_cache = {}      # type: tp.Dict[K, bool]

    def get_value_block(self, key: K) -> V:
        """
        Get a value using value_getter. Block until it's available. Store it into the cache.
        """
        future = self.value_getter_executor.submit(self.value_getter, key)
        try:
            value = future.result()
        except KeyError:
            self.try_delete(key)
            raise
        self[key] = value
        return value

    def schedule_a_fetch(self, key: K) -> None:
        """
        Schedule a value refresh for given key
        """
        future = self.value_getter_executor.submit(self.value_getter, key)

        def on_done_callback(fut: Future) -> None:
            try:
                result = fut.result()
            except KeyError:
                self.try_delete(key)
            self[key] = result

        future.add_done_callback(on_done_callback)

    @silence_excs(KeyError)
    def try_delete(self, key: K) -> None:
        """
        Syntactic sugar for


        >>> try:
        >>>   del self[key]
        >>> except KeyError:
        >>>   pass
        """
        del self[key]

    def __getitem__(self, item: K) -> V:
        if item not in self.data:
            return self.get_value_block(item)

        timestamp = self.timestamp_data[item]
        now = time.monotonic()
        if now - timestamp > self.expiration_interval:
            return self.get_value_block(item)
        elif now - timestamp > self.stale_interval:
            self.schedule_a_fetch(item)
            return self.data[item]
        else:
            return self.data[item]

    def __delitem__(self, key):
        del self.data[key]
        del self.timestamp_data[key]

    def __setitem__(self, key, value):
        """
        Store a value with current timestamp
        """
        self.data[key] = value
        self.timestamp_data[key] = time.monotonic()
