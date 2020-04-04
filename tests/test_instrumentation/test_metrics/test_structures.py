import unittest

from satella.instrumentation.metrics import getMetric

import time
from satella.instrumentation.metrics.structures import MetrifiedThreadPoolExecutor


def wait():
    time.sleep(2)


class TestThreadPoolExecutor(unittest.TestCase):
    def test_metrified_thread_pool_executor(self):
        waiting_summary = getMetric('mtpe.summary', 'summary')
        executing_summary = getMetric('mtpe.executing', 'summary')
        callable_metric = getMetric('mtpe.outstanding', 'callable')

        mtpe = MetrifiedThreadPoolExecutor(max_workers=2, time_spent_waiting=waiting_summary,
                                           time_spent_executing=executing_summary,
                                           waiting_tasks=callable_metric)

        mtpe.submit(wait)
        time.sleep(0.1)
        self.assertEqual(callable_metric.to_metric_data().values[0].value, 0)
        mtpe.submit(wait)
        mtpe.submit(wait)
        time.sleep(0.1)
        self.assertEqual(callable_metric.to_metric_data().values[0].value, 1)
