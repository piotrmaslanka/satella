import unittest

from satella.instrumentation.metrics import getMetric

import time
from satella.instrumentation.metrics.structures import MetrifiedThreadPoolExecutor, \
    MetrifiedCacheDict
from .test_metrics import choose


def wait():
    time.sleep(2)


class TestThreadPoolExecutor(unittest.TestCase):
    def test_metrified_cache_dict(self):
        cache_hits = getMetric('cachedict.hits', 'cps', time_unit_vectors=[10])
        cache_miss = getMetric('cachedict.miss', 'cps', time_unit_vectors=[10])
        value = 2

        def getter(key):
            nonlocal value
            if value is None:
                raise KeyError()
            else:
                return value

        mcd = MetrifiedCacheDict(1, 2, getter, cache_hits_cps=cache_hits,
                                 cache_miss_cps=cache_miss)
        mcd[2]
        self.assertEqual(next(iter(cache_hits.to_metric_data().values)).value, 0)
        self.assertEqual(next(iter(cache_miss.to_metric_data().values)).value, 1)
        mcd[2]
        self.assertEqual(next(iter(cache_hits.to_metric_data().values)).value, 1)
        self.assertEqual(next(iter(cache_miss.to_metric_data().values)).value, 1)

    def test_metrified_thread_pool_executor(self):
        waiting_summary = getMetric('mtpe.summary', 'summary')
        executing_summary = getMetric('mtpe.executing', 'summary')
        callable_metric = getMetric('mtpe.outstanding', 'callable')

        mtpe = MetrifiedThreadPoolExecutor(max_workers=2, time_spent_waiting=waiting_summary,
                                           time_spent_executing=executing_summary,
                                           waiting_tasks=callable_metric)

        mtpe.submit(wait)
        time.sleep(0.1)
        self.assertEqual(next(iter(callable_metric.to_metric_data().values)).value, 0)
        mtpe.submit(wait)
        fr = mtpe.submit(wait)
        time.sleep(0.1)
        self.assertEqual(next(iter(callable_metric.to_metric_data().values)).value, 1)
        fr.result()
        self.assertIn(choose('.count', executing_summary.to_metric_data()).value, {2, 3})
        self.assertEqual(choose('.count', waiting_summary.to_metric_data()).value, 3)
