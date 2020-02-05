import time
import unittest
import logging

from satella.instrumentation.metrics import getMetric, DEBUG, RUNTIME, INHERIT
from satella.instrumentation.metrics.exporters import json_to_prometheus

logger = logging.getLogger(__name__)


class TestMetric(unittest.TestCase):

    def tearDown(self):
        getMetric('').reset()

    def test_quantile_children(self):
        metric = getMetric('my_metric', 'quantile', quantiles=[0.5])
        metric.runtime(10.0, label='value')
        metric.runtime(20.0, label='wtf')
        metr = metric.to_json()
        self.assertEqual(metr['sum'][0]['_'], 15.0)
        self.assertEqual(metr['count']['_'], 2)
        self.assertEqual(metr['total']['_'], 30.0)
        self.assertIn('_timestamp', metr['total'])

    def test_quantile(self):
        metric = getMetric('root.test.ExecutionTime', 'quantile', quantiles=[0.5, 0.95],
                           count_calls=False, enable_timestamp=False)
        for i in range(9):
            metric.runtime(10.0)
        metric.runtime(15.0)

        self.assertEqual(metric.to_json(), [{'quantile': 0.5, '_': 10.0},
                                            {'quantile': 0.95, '_': 12.749999999999995}])

    def test_labels(self):
        metric = getMetric('root.test.FloatValue', 'float', enable_timestamp=False)
        metric.runtime(2, label='value')
        metric.runtime(3, label='key')

        self.assertEqual(metric.to_json(), [{'label': 'value', '_': 2}, {'label': 'key', '_': 3}])

    def test_base_metric(self):
        metric = getMetric('root.test.StringValue', 'string', enable_timestamp=False)
        metric.runtime('data')

        metric2 = getMetric('root.test.FloatValue', 'float', enable_timestamp=False)
        metric2.runtime(2.0)

        metric3 = getMetric('root.test.IntValue', 'int', enable_timestamp=False)
        metric3.runtime(3)

        root_metric = getMetric('', enable_timestamp=False)

        self.assertEqual(root_metric.to_json(), {
            'root': {
                'test': {
                    'StringValue': {'_': 'data'},
                    'FloatValue': {'_': 2.0},
                    'IntValue': {'_': 3}
                }
            }
        })

    def test_wait(self):
        metric = getMetric('test', 'quantile', quantiles=[0.5])
        @metric.measure()
        def wait(throw=False):
            time.sleep(1)
            if throw:
                raise ValueError('sample exception')
        wait()
        self.assertRaises(ValueError, lambda: wait(throw=True))
        self.assertGreaterEqual(metric.to_json()['_'][0]['_'], 1)

    def test_counter(self):
        counter = getMetric('counter', 'counter', enable_timestamp=False)
        counter.runtime(1, service='user')
        counter.runtime(2, service='session')
        counter.runtime(1, service='user')
        self.assertEqual({'_': [{'service': 'user', '_': 2}, {'service': 'session', '_': 2}],
                          'sum': {'_': 4}}, counter.to_json())

    def test_counter_count_calls(self):
        counter = getMetric('counter', 'counter', enable_timestamp=False, count_calls=True)
        counter.runtime(1, service='user')
        counter.runtime(2, service='session')
        counter.runtime(1, service='user')
        self.assertEqual({'_': [{'service': 'user', '_': {'_': 2, 'service': 'user'}, 'count': {'_': 2, 'service': 'user'}},
                                {'service': 'session', '_': {'_': 2, 'service': 'session'}, 'count': {'_': 1, 'service': 'session'}}],
                          'sum': {'_': 4}, 'count': {'_': 3}}, counter.to_json())

    def test_base_metric(self):
        metric2 = getMetric('root.test.FloatValue', 'float', DEBUG, enable_timestamp=False)
        metric2.runtime(2.0)
        metric2.debug(1.0)

        metric3 = getMetric('root.test.IntValue', 'int', RUNTIME, enable_timestamp=False)

        metric3.runtime(3)
        metric3.debug(2)

        root_metric = getMetric('')

        self.assertEqual({
            'root': {
                'test': {
                    'FloatValue': {'_': 1.0},
                    'IntValue': {'_': 3}
                }
            }
        }, root_metric.to_json())

    def testInheritance(self):
        metric = getMetric('root.test.FloatValue', 'float', INHERIT, enable_timestamp=False)
        metric.runtime(2.0)
        metric_parent = getMetric('root.test', enable_timestamp=False)

        self.assertEqual(getMetric('', enable_timestamp=False).to_json(), {
            'root': {
                'test': {
                    'FloatValue': {'_': 2.0},
                }
            }
        })

        metric_parent.level = RUNTIME
        metric.debug(3.0)

        self.assertEqual(getMetric('').to_json(), {
            'root': {
                'test': {
                    'FloatValue': {'_': 2.0},
                }
            }
        })

    def test_labels(self):
        metric = getMetric('root.IntValue', 'int', labels={'k': 2}, enable_timestamp=False)
        metric.runtime(3)
        self.assertEqual(metric.to_json(), {'k': 2, '_': 3})

    def test_cps(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1, 2], enable_timestamp=False)
        metric.runtime()
        self.assertEqual([1, 2], metric.time_unit_vectors)
        self.assertEqual([{'period': 1, '_': 1}, {'period': 2, '_': 1}], metric.to_json())
        metric.runtime()
        self.assertEqual([{'period': 1, '_': 2}, {'period': 2, '_': 2}], metric.to_json())
        time.sleep(1.2)
        self.assertEqual([{'period': 1, '_': 0}, {'period': 2, '_': 2}], metric.to_json())

    def test_cps_labels(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1], enable_timestamp=False)
        metric.runtime(key='value')
        self.assertEqual({'_': [{'period': 1, '_': 1, 'key': 'value'}],
                          'sum': [{'period': 1, '_': 1}]}, metric.to_json())
