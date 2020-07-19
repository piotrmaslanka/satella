import time
import typing as tp
from satella.coding.structures import CacheDict
from satella.time import measure
from .. import Metric
from ..metric_types import ClicksPerTimeUnitMetric


class MetrifiedCacheDict(CacheDict):
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
                 cache_hits: tp.Optional[Metric] = None,
                 cache_miss: tp.Optional[Metric] = None,
                 refreshes: tp.Optional[Metric] = None,
                 how_long_refresh_takes: tp.Optional[Metric] = None):
        if refreshes or how_long_refresh_takes:
            def value_getter_replacement(item):
                with measure() as measurement:
                    try:
                        return value_getter(item)
                    finally:
                        if self.refreshes:
                            self.refreshes.runtime(+1)
                        if self.how_long_refresh_takes:
                            self.how_long_refresh_takes.runtime(measurement())

            value_getter = value_getter_replacement

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
