import time
import unittest
import logging
import inspect

from satella.instrumentation.metrics import getMetric, DEBUG, RUNTIME, INHERIT, MetricData, \
    MetricDataCollection

logger = logging.getLogger(__name__)


def choose(postfix: str, mdc: MetricDataCollection, labels=None) -> MetricData:
    for child in mdc.values:
        if child.name.endswith(postfix) and child.labels == (labels or {}):
            return child


class TestMetric(unittest.TestCase):

    def setUp(self) -> None:
        getMetric('').reset()

    def test_quantile_measure_generator(self):
        metric = getMetric('my_metric', 'quantile', quantiles=[0.5])
        @metric.measure()
        def generator():
            yield 2
            time.sleep(1)
            yield 3
        for v in generator():
            pass
        self.assertTrue(inspect.isgeneratorfunction(generator))
        self.assertGreaterEqual(next(iter(metric.to_metric_data().values)).value, 1)

    def test_quantile_children(self):
        metric = getMetric('my_metric', 'quantile', quantiles=[0.5], enable_timestamp=True)
        metric.runtime(10.0, label='value')
        metric.runtime(20.0, label='wtf')
        metr = metric.to_metric_data()
        self.assertEqual(choose('sum', metr).value, 30.0)
        self.assertEqual(choose('count', metr).value, 2)
        self.assertEqual(choose('total', metr, {'quantile': 0.5}).value, 15.0)
        self.assertTrue(all(x.timestamp is not None for x in metr.values))

    def test_quantile(self):
        metric = getMetric('root.test.ExecutionTime', 'quantile', quantiles=[0.5, 0.95],
                           count_calls=False, enable_timestamp=False)
        for i in range(9):
            metric.runtime(10.0)
        metric.runtime(15.0)

        self.assertTrue(MetricDataCollection(MetricData('ExecutionTime', 10.0, {'quantile': 0.5}),
                                             MetricData('ExecutionTime', 12.749999999999995, {'quantile': 0.95})).strict_eq(metric.to_metric_data()))

    def test_labels(self):
        metric = getMetric('root.test.FloatValue', 'float', enable_timestamp=False)
        metric.runtime(2, label='value')
        metric.runtime(3, label='key')

        self.assertTrue(MetricDataCollection(MetricData('root.test.FloatValue', 2, {'label': 'value'}),
                                             MetricData('root.test.FloatValue', 3, {'label': 'key'})).strict_eq(metric.to_metric_data()))

    def test_base_metric(self):
        metric1 = getMetric('root.test.FloatValue', 'float', enable_timestamp=False)
        metric1.runtime(2.0)

        metric2 = getMetric('root.test.IntValue', 'int', enable_timestamp=False)
        metric2.runtime(3)

        root_metric = getMetric('', enable_timestamp=False)

        self.assertTrue(root_metric.to_metric_data().strict_eq(
            MetricData('root.test.FloatValue', 2),
            MetricData('root.test.IntValue', 3)))

    def test_wait(self):
        metric = getMetric('test', 'quantile', quantiles=[0.5])
        @metric.measure()
        def wait(throw=False):
            time.sleep(1)
            if throw:
                raise ValueError('sample exception')
        wait()
        self.assertFalse(inspect.isgeneratorfunction(wait))
        self.assertRaises(ValueError, lambda: wait(throw=True))
        self.assertGreaterEqual(next(iter(metric.to_metric_data().values)).value, 1)

    def test_counter(self):
        counter = getMetric('counter', 'counter', enable_timestamp=False)
        counter.runtime(1, service='user')
        counter.runtime(2, service='session')
        counter.runtime(1, service='user')
        self.assertTrue(MetricDataCollection(MetricData('counter', 2, {'service': 'user'}),
                                             MetricData('counter', 2, {'service': 'session'}),
                                             MetricData('counter.sum', 4)).strict_eq(counter.to_metric_data()))

    def test_counter_count_calls(self):
        counter = getMetric('counter', 'counter', enable_timestamp=False, count_calls=True)
        counter.runtime(1, service='user')
        counter.runtime(2, service='session')
        counter.runtime(1, service='user')
        self.assertTrue(MetricDataCollection(MetricData('counter', 2, {'service': 'user'}),
                                             MetricData('counter.count', 2, {'service': 'user'}),
                                             MetricData('counter', 2, {'service': 'session'}),
                                             MetricData('counter.count', 1, {'service': 'session'}),
                                             MetricData('counter.sum', 4),
                                             MetricData('counter.count', 3)).strict_eq(counter.to_metric_data()))

    def test_base_metric(self):
        metric2 = getMetric('root.test.FloatValue', 'float', DEBUG, enable_timestamp=False)
        metric2.runtime(2.0)
        metric2.debug(1.0)

        metric3 = getMetric('root.test.IntValue', 'int', RUNTIME, enable_timestamp=False)
        self.assertEqual(metric3.get_fully_qualified_name(), 'root.test.IntValue')
        metric3.runtime(3)
        metric3.debug(2)

        root_metric = getMetric('')

        self.assertTrue(
            MetricDataCollection(
                MetricData('root.test.FloatValue', 1.0),
                MetricData('root.test.IntValue', 3)).strict_eq(root_metric.to_metric_data()))

    def testInheritance(self):
        metric = getMetric('root.test.FloatValue', 'float', INHERIT, enable_timestamp=False)
        metric.runtime(2.0)
        metric_parent = getMetric('root.test', enable_timestamp=False)
        self.assertEqual(metric_parent.get_fully_qualified_name(), 'root.test')
        logger.warning(f'{getMetric().to_metric_data().values}')
        self.assertTrue(getMetric().to_metric_data().strict_eq(
            MetricDataCollection(MetricData('root.test.FloatValue', 2.0))))

        metric_parent.level = RUNTIME
        metric.debug(3.0)

        self.assertTrue(getMetric('', enable_timestamp=False).to_metric_data().strict_eq(
            MetricDataCollection(MetricData('root.test.FloatValue', 2.0))))

    def test_labels(self):
        metric = getMetric('root.IntValue', 'int', labels={'k': 2}, enable_timestamp=False)
        metric.runtime(3)
        self.assertTrue(MetricDataCollection(MetricData('IntValue', 3, {'k': 2})).strict_eq(metric.to_metric_data()))

    def test_cps(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1, 2], enable_timestamp=False)
        self.assertEqual(metric.name, 'CPSValue')
        metric.runtime()
        self.assertEqual([1, 2], metric.time_unit_vectors)
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 1, {'period': 1}),
                                             MetricData('CPSValue', 1, {'period': 2})).strict_eq(metric.to_metric_data()))
        metric.runtime()
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 2, {'period': 1}),
                                             MetricData('CPSValue', 2, {'period': 2})).strict_eq(metric.to_metric_data()))
        time.sleep(1.2)
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 0, {'period': 1}),
                                             MetricData('CPSValue', 2, {'period': 2})).strict_eq(metric.to_metric_data()))

    def test_cps_labels(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1], enable_timestamp=False)
        metric.runtime(key='value')
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 1, {'period': 1, 'key': 'value'}),
                                             MetricData('CPSValue.total', 1, {'period': 1})).strict_eq(metric.to_metric_data()))
