import inspect
import logging
import time
import unittest

from satella.coding.sequences import n_th

from satella.exceptions import MetricAlreadyExists
from satella.instrumentation.metrics import getMetric, MetricLevel, MetricData, \
    MetricDataCollection, AggregateMetric, LabeledMetric

logger = logging.getLogger(__name__)


def choose(postfix: str, mdc: MetricDataCollection, labels=None) -> MetricData:
    for child in mdc.values:
        if child.name.endswith(postfix) and child.labels == (labels or {}):
            return child


class TestMetric(unittest.TestCase):

    def test_child_metrics(self):
        """A RUNTIME parent does not display DEBUG child's metric"""
        parent = getMetric('test.child.metric', metric_level=MetricLevel.RUNTIME)
        child = getMetric('test.child.metric.kid', 'int', metric_level=MetricLevel.DEBUG)
        child.runtime(2)
        data = parent.to_metric_data()
        kid = choose('.kid', data)
        self.assertIsNone(kid)

    def test_default_float(self):
        met = getMetric('test.float', 'float')
        data = met.to_metric_data()
        v = choose('', data)
        self.assertEqual(v.value, 0.0)

    def test_uptime_metric(self):
        up_metric = getMetric('uptime.metric', 'uptime')
        time.sleep(1)
        self.assertGreaterEqual(n_th(up_metric.to_metric_data().values).value, 1)

    def test_forbidden_characters(self):
        self.assertRaises(ValueError, lambda: getMetric('forbidden-characters', 'int'))

    def test_labeled_metric_with_callable(self):
        m1 = getMetric('lmc1', 'callable')
        lm = LabeledMetric(m1, key='value')
        lm.callable = lambda: 0

        self.assertEqual(choose('lmc1', m1.to_metric_data(), {'key': 'value'}).value, 0)

    def test_aggregate(self):
        m1 = getMetric('am1', 'summary')
        m2 = getMetric('am2', 'histogram')
        am = AggregateMetric(m1, m2)
        am.runtime(2)
        data = choose('.count', m1.to_metric_data())
        self.assertEqual(data.value, 1)
        data = choose('.count', m2.to_metric_data())
        self.assertEqual(data.value, 1)

    def test_callable(self):
        callable_ = getMetric('callable', 'callable', value_getter=lambda: 5.0)
        self.assertEqual(list(callable_.to_metric_data().values)[0].value, 5.0)

    def test_linkfail(self):
        d = {'online': False, 'offline': False}

        def on_online(address, labels):
            d['online'] = True

        def on_offline(address, labels):
            d['offline'] = True

        linkfail = getMetric('linkfail', 'linkfail', consecutive_failures_to_offline=10,
                             consecutive_successes_to_online=10, callback_on_online=on_online,
                             callback_on_offline=on_offline)

        for i in range(10):
            linkfail.runtime(False)

        self.assertEqual(choose('.status', linkfail.to_metric_data()).value, 0)

        for i in range(10):
            linkfail.runtime(True)

        self.assertTrue(d['online'])
        self.assertTrue(d['offline'])

        self.assertEqual(choose('.status', linkfail.to_metric_data()).value, 1)

    def setUp(self) -> None:
        getMetric('').reset()

    def test_embedded_submetrics_labels_getter(self):
        metric = getMetric('embedded_submetrics_test', 'int')
        metric.runtime(1, label='value')
        self.assertTrue(metric.get_specific_metric_data({'label': 'value'}).values)

    def test_histogram(self):
        metric = getMetric('test_histogram', 'histogram')
        metric.runtime(1)
        metric.runtime(2.6)
        metric_data = metric.to_metric_data()
        self.assertEqual(choose('', metric_data, {'le': 2.5, 'ge': 1.0}).value, 1)
        self.assertEqual(choose('sum', metric_data).value, 3.6)
        self.assertEqual(choose('count', metric_data).value, 2)

    def test_histogram_children(self):
        metric = getMetric('test_histogram', 'histogram')
        metric.runtime(1, label='value')
        metric.runtime(2.6, label='value')
        metric_data = metric.to_metric_data()
        self.assertEqual(choose('', metric_data, {'le': 2.5, 'ge': 1.0, 'label': 'value'}).value, 1)
        self.assertEqual(choose('sum', metric_data, {'label': 'value'}).value, 3.6)
        self.assertEqual(choose('count', metric_data, {'label': 'value'}).value, 2)
        self.assertEqual(choose('total', metric_data, {'le': 2.5, 'ge': 1.0}).value, 1)
        self.assertEqual(choose('total.sum', metric_data).value, 3.6)
        self.assertEqual(choose('total.count', metric_data).value, 2)

    def test_empty(self):
        metric = getMetric('empty', 'empty')
        self.assertEqual(len(metric.to_metric_data().values), 0)

    def test_metric_already_exists(self):
        getMetric('testmetric2', 'cps')
        try:
            getMetric('testmetric2', 'summary')
        except MetricAlreadyExists as e:
            self.assertEqual(e.name, 'testmetric2')
            self.assertEqual(e.requested_type, 'summary')
            self.assertEqual(e.existing_type, 'cps')
        else:
            self.fail('Exception not raised')

    def test_int_children(self):
        metric = getMetric('test_children_int', 'int')
        metric.runtime(1, label='value')
        should_be_equal_to = MetricDataCollection(
            MetricData('test_children_int', 1, {'label': 'value'}))
        self.assertTrue(metric.to_metric_data().strict_eq(should_be_equal_to))

    def test_quantile_measure_generator(self):
        metric = getMetric('my_metric', 'summary', quantiles=[0.5])

        @metric.measure()
        def generator():
            yield 2
            time.sleep(1)
            yield 3

        for v in generator():
            pass
        self.assertTrue(inspect.isgeneratorfunction(generator))
        self.assertGreaterEqual(next(iter(metric.to_metric_data().values)).value, 1)

    def test_aggregate_metric_measure_generator(self):
        my_metric = getMetric('my_metric', 'summary', quantiles=[0.5])
        metric = AggregateMetric(my_metric)

        @metric.measure()
        def generator():
            yield 2
            time.sleep(1)
            yield 3

        for _ in generator():
            pass
        self.assertTrue(inspect.isgeneratorfunction(generator))
        self.assertGreaterEqual(next(iter(my_metric.to_metric_data().values)).value, 1)

    def test_quantile_context_manager(self):
        metric = getMetric('test_metric', 'summary', quantiles=[0.5])
        with metric.measure():
            time.sleep(1)
        self.assertGreaterEqual(next(iter(metric.to_metric_data().values)).value, 1)

    def test_counter_measure(self):
        metric = getMetric('test2', 'counter')
        with metric.measure():
            time.sleep(2)
        self.assertGreaterEqual(next(iter(metric.to_metric_data().values)).value, 1)

    def test_quantile_children(self):
        metric = getMetric('my_metric', 'summary', quantiles=[0.5], enable_timestamp=True)
        metric.runtime(10.0, label='value')
        metric.runtime(20.0, label='wtf')
        metr = metric.to_metric_data()
        self.assertEqual(choose('sum', metr).value, 30.0)
        self.assertEqual(choose('count', metr).value, 2)
        self.assertEqual(choose('total', metr, {'quantile': 0.5}).value, 15.0)
        self.assertTrue(all(x.timestamp is not None for x in metr.values))

    def test_quantile(self):
        metric = getMetric('root.test.ExecutionTime', 'summary', quantiles=[0.5, 0.95],
                           count_calls=False, enable_timestamp=False)
        for i in range(9):
            metric.runtime(10.0)
        metric.runtime(15.0)

        self.assertTrue(MetricDataCollection(MetricData('ExecutionTime', 10.0, {'quantile': 0.5}),
                                             MetricData('ExecutionTime', 12.749999999999995,
                                                        {'quantile': 0.95})).strict_eq(
            metric.to_metric_data()))

    def test_labels(self):
        metric = getMetric('root.test.FloatValue', 'float', enable_timestamp=False)
        metric.runtime(2, label='value')
        metric.runtime(3, label='key')

        self.assertTrue(
            MetricDataCollection(MetricData('root.test.FloatValue', 2, {'label': 'value'}),
                                 MetricData('root.test.FloatValue', 3, {'label': 'key'})).strict_eq(
                metric.to_metric_data()))

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
        metric = getMetric('test', 'summary', quantiles=[0.5])

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
                                             MetricData('counter.sum', 4)).strict_eq(
            counter.to_metric_data()))

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
                                             MetricData('counter.count', 3)).strict_eq(
            counter.to_metric_data()))

    def test_base_metric(self):
        root_metric = getMetric()
        root_metric.level = MetricLevel.DEBUG
        metric2 = getMetric('root.test.FloatValue', 'float', MetricLevel.DEBUG, enable_timestamp=False)
        metric2.runtime(2.0)
        metric2.debug(1.0)

        metric3 = getMetric('root.test.IntValue', 'int', MetricLevel.RUNTIME, enable_timestamp=False)
        self.assertEqual(metric3.get_fully_qualified_name(), 'root.test.IntValue')
        metric3.runtime(3)
        metric3.debug(2)

        root_metric = getMetric('')

        self.assertTrue(
            MetricDataCollection(
                MetricData('root.test.FloatValue', 1.0),
                MetricData('root.test.IntValue', 3)).strict_eq(root_metric.to_metric_data()))

    def testInheritance(self):
        metric = getMetric('root.test.FloatValue', 'float', MetricLevel.INHERIT,
                           enable_timestamp=False)
        metric.runtime(2.0)
        metric_parent = getMetric('root.test', enable_timestamp=False)
        self.assertEqual(metric_parent.get_fully_qualified_name(), 'root.test')
        self.assertTrue(getMetric().to_metric_data().strict_eq(
            MetricDataCollection(MetricData('root.test.FloatValue', 2.0))))

        metric_parent.level = MetricLevel.RUNTIME
        metric.debug(3.0)

        self.assertTrue(getMetric('', enable_timestamp=False).to_metric_data().strict_eq(
            MetricDataCollection(MetricData('root.test.FloatValue', 2.0))))

    def test_labels(self):
        metric = getMetric('root.IntValue', 'int', labels={'k': 2}, enable_timestamp=False)
        metric.runtime(3)
        self.assertTrue(MetricDataCollection(MetricData('IntValue', 3, {'k': 2})).strict_eq(
            metric.to_metric_data()))

    def test_cps(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1, 2], enable_timestamp=False)
        self.assertEqual(metric.name, 'CPSValue')
        metric.runtime()
        self.assertEqual([1, 2], metric.time_unit_vectors)
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 1, {'period': 1}),
                                             MetricData('CPSValue', 1, {'period': 2})).strict_eq(
            metric.to_metric_data()))
        metric.runtime()
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 2, {'period': 1}),
                                             MetricData('CPSValue', 2, {'period': 2})).strict_eq(
            metric.to_metric_data()))
        time.sleep(1.2)
        self.assertTrue(MetricDataCollection(MetricData('CPSValue', 0, {'period': 1}),
                                             MetricData('CPSValue', 2, {'period': 2})).strict_eq(
            metric.to_metric_data()))

    def test_cps_labels(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1], enable_timestamp=False)
        metric.runtime(key='value')
        self.assertTrue(
            MetricDataCollection(MetricData('CPSValue', 1, {'period': 1, 'key': 'value'}),
                                 MetricData('CPSValue.total', 1, {'period': 1})).strict_eq(
                metric.to_metric_data()))
