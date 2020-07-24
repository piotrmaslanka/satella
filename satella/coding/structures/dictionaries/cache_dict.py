import logging
import time
import typing as tp
from concurrent.futures import ThreadPoolExecutor, Executor, Future

from satella.coding.recast_exceptions import silence_excs

logger = logging.getLogger(__name__)
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
    :param cache_failures_interval: if any other than None is defined, this is the timeout
        for which failed lookups will be cached. By default they won't be cached at all.
    :param time_getter: a routine used to get current time in seconds
    :param default_value_factory: if given, this is the callable that will return values
        that will be given to user instead of throwing KeyError. If not given (default),
        KeyError will be thrown
    """

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> tp.Iterator[K]:
        return iter(self.data)

    def has_info_about(self, key: str) -> bool:
        """
        Is provided key cached, or failure about it is cached?
        """
        if key in self.data:
            try:
                # an additional check, since this is a concurrent data structure and
                # we aren't locking
                return self.time_getter() - self.timestamp_data[key] <= self.expiration_interval
            except KeyError:
                return False

        if self.cache_failures:
            if key in self.cache_missed:
                try:
                    return self.time_getter() - self.timestamp_data[key] <= self.expiration_interval
                except KeyError:
                    return False

        return False

    def __init__(self, stale_interval: float, expiration_interval: float,
                 value_getter: tp.Callable[[K], V],
                 value_getter_executor: tp.Optional[Executor] = None,
                 cache_failures_interval: tp.Optional[float] = None,
                 time_getter: tp.Callable[[], float] = time.monotonic,
                 default_value_factory: tp.Optional[tp.Callable[[], V]] = None):
        assert stale_interval <= expiration_interval, 'Stale interval may not be larger ' \
                                                      'than expiration interval!'
        self.stale_interval = stale_interval
        self.default_value_factory = default_value_factory
        self.expiration_interval = expiration_interval
        self.value_getter = value_getter
        if value_getter_executor is None:
            value_getter_executor = ThreadPoolExecutor(max_workers=4)
        self.value_getter_executor = value_getter_executor
        self.data = {}  # type: tp.Dict[K, V]
        self.timestamp_data = {}  # type: tp.Dict[K, float]
        self.cache_missed = set()  # type: tp.Set[K]
        self.cache_failures = cache_failures_interval is not None
        self.cache_failures_interval = cache_failures_interval
        self.time_getter = time_getter

    def get_value_block(self, key: K) -> V:
        """
        Get a value using value_getter. Block until it's available. Store it into the cache.

        :raises KeyError: the value is not present at all
        """
        future = self.value_getter_executor.submit(self.value_getter, key)
        try:
            value = future.result()
        except KeyError:
            self._on_failure(key)
            if self.default_value_factory:
                return self.default_value_factory()
            else:
                raise
        self[key] = value
        return value

    def _on_failure(self, key: K) -> None:
        """
        Called internally when a KeyError occurs.

        It is expected that invalidate(key) will be always called before
        """
        self.invalidate(key)
        if self.cache_failures:
            self.cache_missed.add(key)
            self.timestamp_data[key] = self.time_getter()

    def schedule_a_fetch(self, key: K) -> Future:
        """
        Schedule a value refresh for given key

        :param key: key to schedule the refresh for
        :return: future that was queued to ask for given key
        """
        future = self.value_getter_executor.submit(self.value_getter, key)

        def on_done_callback(fut: Future) -> None:
            try:
                result = fut.result()
            except KeyError:
                self._on_failure(key)
            else:
                self[key] = result

        future.add_done_callback(on_done_callback)
        return future

    @silence_excs(KeyError)
    def invalidate(self, key: K) -> None:
        """
        Remove all information about given key from the cache

        Syntactic sugar for:

        >>> try:
        >>>   del self[key]
        >>> except KeyError:
        >>>   pass
        """
        del self[key]

    def _on_cache_hit_empty(self, key: K, timestamp: float, now: float) -> V:
        if key in self.cache_missed:
            if now - timestamp > self.cache_failures_interval:
                return self.get_value_block(key)
            else:
                if self.default_value_factory:
                    return self.default_value_factory()
                else:
                    raise KeyError('Cached a miss')

    def __getitem__(self, key: K) -> V:
        if key not in self.data and key not in self.cache_missed:
            return self.get_value_block(key)

        timestamp = self.timestamp_data[key]
        now = time.monotonic()

        if key in self.cache_missed:
            return self._on_cache_hit_empty(key, timestamp, now)
        else:
            return self._on_cache_hit(key, timestamp, now)

    def _on_cache_hit(self, key: K, timestamp: float, now: float) -> V:
        if now - timestamp > self.expiration_interval:
            return self.get_value_block(key)
        elif now - timestamp > self.stale_interval:
            self.schedule_a_fetch(key)
            return self.data[key]
        else:
            return self.data[key]

    def __delitem__(self, key: K) -> None:
        del self.data[key]
        del self.timestamp_data[key]
        with silence_excs(KeyError):
            self.cache_missed.remove(key)

    def __setitem__(self, key: K, value: V) -> None:
        """
        Store a value with current timestamp
        """
        self.data[key] = value
        self.timestamp_data[key] = self.time_getter()
        with silence_excs(KeyError):
            self.cache_missed.remove(key)
