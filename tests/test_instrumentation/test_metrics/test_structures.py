import unittest

from satella.coding.sequences import n_th
from satella.instrumentation.metrics import getMetric

import time
from satella.instrumentation.metrics.structures import MetrifiedThreadPoolExecutor, \
    MetrifiedCacheDict, MetrifiedLRUCacheDict, MetrifiedExclusiveWritebackCache
from .test_metrics import choose


def wait():
    time.sleep(2)


class TestThreadPoolExecutor(unittest.TestCase):
    def test_exclusive_writeback_cache(self):
        cache_hits = getMetric('wbc.cachedict.hits', 'counter')
        cache_miss = getMetric('wbc.cachedict.miss', 'counter')
        entries_waiting = getMetric('wbc.cachedict.waiting', 'callable')
        a = {5: 3, 4: 2, 1: 0}
        b = {'no_calls': 0}

        def setitem(k, v):
            nonlocal a, b
            b['no_calls'] += 1
            a[k] = v

        def getitem(k):
            nonlocal a, b
            b['no_calls'] += 1
            return a[k]

        def delitem(k):
            nonlocal a, b
            b['no_calls'] += 1
            del a[k]

        wbc = MetrifiedExclusiveWritebackCache(setitem, getitem, delitem,
                                               cache_hits=cache_hits,
                                               cache_miss=cache_miss,
                                               entries_waiting=entries_waiting)
        self.assertEqual(wbc[5], 3)
        self.assertEqual(b['no_calls'], 1)
        self.assertRaises(KeyError, lambda: wbc[-1])
        self.assertEqual(b['no_calls'], 2)
        self.assertEqual(wbc[5], 3)
        self.assertEqual(b['no_calls'], 2)
        self.assertEqual(n_th(cache_miss.to_metric_data().values).value, 2)
        self.assertEqual(n_th(cache_hits.to_metric_data().values).value, 1)
        wbc[5] = 2
        wbc.sync()
        self.assertEqual(a[5], 2)
        self.assertEqual(b['no_calls'], 3)
        del wbc[4]
        wbc.sync()
        self.assertRaises(KeyError, lambda: a[4])

    def test_metrified_cache_dict(self):
        cache_hits = getMetric('cachedict.hits', 'counter')
        cache_miss = getMetric('cachedict.miss', 'counter')
        refreshes = getMetric('refreshes', 'counter')
        how_long_takes = getMetric('how_long_takes', 'summary')
        value = 2

        def getter(key):
            nonlocal value
            time.sleep(0.5)
            if value is None:
                raise KeyError()
            else:
                return value

        mcd = MetrifiedCacheDict(1, 2, getter, cache_hits=cache_hits,
                                 cache_miss=cache_miss,
                                 refreshes=refreshes,
                                 how_long_refresh_takes=how_long_takes)
        mcd[2]
        self.assertEqual(n_th(cache_hits.to_metric_data().values).value, 0)
        self.assertEqual(n_th(cache_miss.to_metric_data().values).value, 1)
        self.assertEqual(n_th(refreshes.to_metric_data().values).value, 1)
        self.assertGreaterEqual(n_th(how_long_takes.to_metric_data().values).value, 0.5)
        mcd[2]
        self.assertEqual(n_th(cache_hits.to_metric_data().values).value, 1)
        self.assertEqual(n_th(cache_miss.to_metric_data().values).value, 1)
        self.assertEqual(n_th(refreshes.to_metric_data().values).value, 1)

    def test_metrified_lru_cache_dict(self):
        cache_hits = getMetric('lrucachedict.hits', 'counter')
        cache_miss = getMetric('lrucachedict.miss', 'counter')
        refreshes = getMetric('lrurefreshes', 'counter')
        evictions = getMetric('lruevictions', 'counter')
        how_long_takes = getMetric('lruhow_long_takes', 'summary')
        value = 2

        def getter(key):
            nonlocal value
            time.sleep(0.5)
            if value is None:
                raise KeyError()
            else:
                return value

        mcd = MetrifiedLRUCacheDict(1, 2, getter, cache_hits=cache_hits,
                                 cache_miss=cache_miss,
                                 refreshes=refreshes,
                                 how_long_refresh_takes=how_long_takes,
                                 evictions=evictions,
                                 max_size=2)
        mcd[2]
        self.assertEqual(n_th(cache_hits.to_metric_data().values).value, 0)
        self.assertEqual(n_th(cache_miss.to_metric_data().values).value, 1)
        self.assertEqual(n_th(refreshes.to_metric_data().values).value, 1)
        self.assertGreaterEqual(n_th(how_long_takes.to_metric_data().values).value, 0.5)
        mcd[2]
        self.assertEqual(n_th(cache_hits.to_metric_data().values).value, 1)
        self.assertEqual(n_th(cache_miss.to_metric_data().values).value, 1)
        self.assertEqual(n_th(refreshes.to_metric_data().values).value, 1)
        mcd[3]
        self.assertEqual(n_th(evictions.to_metric_data().values).value, 0)
        mcd[4]
        self.assertEqual(n_th(evictions.to_metric_data().values).value, 1)

    def test_metrified_thread_pool_executor(self):
        waiting_summary = getMetric('mtpe.summary', 'summary')
        executing_summary = getMetric('mtpe.executing', 'summary')
        callable_metric = getMetric('mtpe.outstanding', 'callable')

        mtpe = MetrifiedThreadPoolExecutor(max_workers=2, time_spent_waiting=waiting_summary,
                                           time_spent_executing=executing_summary,
                                           waiting_tasks=callable_metric)

        mtpe.submit(wait)
        time.sleep(0.1)
        self.assertEqual(n_th(callable_metric.to_metric_data().values).value, 0)
        mtpe.submit(wait)
        fr = mtpe.submit(wait)
        time.sleep(0.1)
        self.assertEqual(n_th(callable_metric.to_metric_data().values).value, 1)
        fr.result()
        self.assertIn(choose('.count', executing_summary.to_metric_data()).value, {2, 3})
        self.assertEqual(choose('.count', waiting_summary.to_metric_data()).value, 3)
