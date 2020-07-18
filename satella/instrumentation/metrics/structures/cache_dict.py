import time
import typing as tp
from satella.coding.structures import CacheDict
from .. import Metric
from ..metric_types import ClicksPerTimeUnitMetric


class MetrifiedCacheDict(CacheDict):
    """
    A CacheDict with metrics!

    :param cache_hits_cps: a metric that will be ticked each time there's a cache hit
    :param cache_miss_cps: a metric that will be ticked each time there's a cache miss
    :param refreshes_cps: a metric that will be ticked each refresh (ie. call to value_getter)
    :param how_long_refresh_takes: a metric that will be ticked with time value_getter took
    """
    def __init__(self, stale_interval, expiration_interval, value_getter,
                 value_getter_executor=None, cache_failures_interval=None,
                 time_getter=time.monotonic,
                 default_value_factory=None,
                 cache_hits_cps: tp.Optional[ClicksPerTimeUnitMetric] = None,
                 cache_miss_cps: tp.Optional[ClicksPerTimeUnitMetric] = None,
                 refreshes_cps: tp.Optional[ClicksPerTimeUnitMetric] = None,
                 how_long_refresh_takes: tp.Optional[Metric] = None):
        super().__init__(stale_interval, expiration_interval, value_getter,
                         value_getter_executor, cache_failures_interval, time_getter,
                         default_value_factory)
        self.cache_hits_cps = cache_hits_cps
        self.cache_miss_cps = cache_miss_cps
        self.refreshes_cps = refreshes_cps
        self.how_long_refresh_takes = how_long_refresh_takes

    def __getitem__(self, item):
        if self.has_info_about(item):
            if self.cache_hits_cps:
                self.cache_hits_cps.runtime()
        else:
            if self.cache_miss_cps:
                self.cache_miss_cps.runtime()
        return super().__getitem__(item)

    def schedule_a_fetch(self, key):
        self.refreshes_cps.runtime()
        time_start = self.time_getter()
        fut = super().schedule_a_fetch(key)

        def on_done_callback(future):
            elapsed = self.time_getter() - time_start
            self.how_long_refresh_takes.runtime(elapsed)

        if self.how_long_refresh_takes:
            fut.add_done_callback(on_done_callback)
        return fut
