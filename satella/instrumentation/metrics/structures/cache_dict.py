import logging
import time
import typing as tp

from satella.coding.structures import CacheDict, LRUCacheDict, ExclusiveWritebackCache
from satella.coding.typing import K, V
from .. import Metric
from ..metric_types.callable import CallableMetric
from ..metric_types.counter import CounterMetric
from ..metric_types.measurable_mixin import MeasurableMixin

logger = logging.getLogger(__name__)


class MetrifiedCacheDict(CacheDict[K, V]):
    """
    A CacheDict with metrics!

    :param cache_hits: a counter metric that will be updated with +1 each time there's a cache hit
    :param cache_miss: a counter metric that will be updated with +1 each time there's a cache miss
    :param refreshes: a metric that will be updated with +1 each time there's a cache refresh
    :param how_long_refresh_takes: a metric that will be ticked with time value_getter took
    """

    def __init__(self, stale_interval, expiration_interval, value_getter,
                 value_getter_executor=None, cache_failures_interval=None,
                 time_getter=time.monotonic,
                 default_value_factory=None,
                 cache_hits: tp.Optional[CounterMetric] = None,
                 cache_miss: tp.Optional[CounterMetric] = None,
                 refreshes: tp.Optional[CounterMetric] = None,
                 how_long_refresh_takes: tp.Optional[MeasurableMixin] = None):
        if refreshes:
            old_value_getter = value_getter

            def value_getter_replacement(item):
                try:
                    return old_value_getter(item)
                finally:
                    if self.refreshes:
                        self.refreshes.runtime(+1)

            value_getter = value_getter_replacement

        if how_long_refresh_takes:
            value_getter = how_long_refresh_takes.measure(value_getter=time_getter)(value_getter)

        super().__init__(stale_interval, expiration_interval, value_getter,
                         value_getter_executor, cache_failures_interval, time_getter,
                         default_value_factory)
        self.cache_hits = cache_hits
        self.cache_miss = cache_miss
        self.refreshes = refreshes
        self.how_long_refresh_takes = how_long_refresh_takes

    def __getitem__(self, item):
        if self.has_info_about(item):
            if self.cache_hits:
                self.cache_hits.runtime(+1)
        else:
            if self.cache_miss:
                self.cache_miss.runtime(+1)
        return super().__getitem__(item)


class MetrifiedLRUCacheDict(LRUCacheDict[K, V]):
    """
    A LRUCacheDict with metrics!

    :param cache_hits: a counter metric that will be updated with +1 each time there's a cache hit
    :param cache_miss: a counter metric that will be updated with +1 each time there's a cache miss
    :param refreshes: a metric that will be updated with +1 each time there's a cache refresh
    :param how_long_refresh_takes: a metric that will be ticked with time value_getter took
    """

    def __init__(self, stale_interval: float, expiration_interval: float,
                 value_getter, value_getter_executor=None,
                 cache_failures_interval=None,
                 time_getter=time.monotonic,
                 default_value_factory=None,
                 max_size: int = 100,
                 cache_hits: tp.Optional[Metric] = None,
                 cache_miss: tp.Optional[Metric] = None,
                 refreshes: tp.Optional[Metric] = None,
                 how_long_refresh_takes: tp.Optional[MeasurableMixin] = None,
                 evictions: tp.Optional[Metric] = None,
                 **kwargs):
        if refreshes:
            old_value_getter = value_getter

            def value_getter_replacement(item):
                try:
                    return old_value_getter(item)
                finally:
                    if self.refreshes:
                        self.refreshes.runtime(+1)

            value_getter = value_getter_replacement

        if how_long_refresh_takes:
            value_getter = how_long_refresh_takes.measure(value_getter=time_getter)(value_getter)

        super().__init__(stale_interval, expiration_interval, value_getter,
                         value_getter_executor, cache_failures_interval, time_getter,
                         default_value_factory, max_size=max_size)
        self.cache_hits = cache_hits
        self.cache_miss = cache_miss
        self.refreshes = refreshes
        self.evictions = evictions
        self.how_long_refresh_takes = how_long_refresh_takes

    def evict(self):
        self.evictions.runtime(+1)
        super().evict()

    def __getitem__(self, item):
        if self.has_info_about(item):
            if self.cache_hits:
                self.cache_hits.runtime(+1)
        else:
            if self.cache_miss:
                self.cache_miss.runtime(+1)
        return super().__getitem__(item)


class MetrifiedExclusiveWritebackCache(ExclusiveWritebackCache[K, V]):
    __slots__ = ('cache_miss', 'cache_hits')

    def __init__(self, *args,
                 cache_hits: tp.Optional[CounterMetric] = None,
                 cache_miss: tp.Optional[CounterMetric] = None,
                 entries_waiting: tp.Optional[CallableMetric] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_miss = cache_miss
        self.cache_hits = cache_hits
        if entries_waiting is not None:
            entries_waiting.callable = self.get_queue_length()

    def __getitem__(self, item):
        if item in self.in_cache:
            if self.cache_hits:
                self.cache_hits.runtime(+1)
        else:
            if self.cache_miss:
                self.cache_miss.runtime(+1)
        return super().__getitem__(item)
