import time
import unittest
import logging

from satella.instrumentation.metrics import getMetric, DEBUG, RUNTIME, INHERIT

logger = logging.getLogger(__name__)


class TestMetric(unittest.TestCase):

    def tearDown(self):
        getMetric('').reset()

    def test_percentile_children(self):
        metric = getMetric('my_metric', 'percentile', percentiles=[0.5])
        metric.runtime(10.0, label='value')
        metric.runtime(20.0, label='wtf')
        metr = metric.to_json()
        self.assertEqual(metr['sum'][0]['_'], 15.0)
        self.assertEqual(metr['count']['_'], 2)
        self.assertEqual(metr['total']['_'], 30.0)

    def test_percentile(self):
        metric = getMetric('root.test.ExecutionTime', 'percentile', percentiles=[0.5, 0.95],
                           count_calls=False)
        for i in range(9):
            metric.runtime(10.0)
        metric.runtime(15.0)

        self.assertEqual(metric.to_json(), [{'quantile': 0.5, '_': 10.0},
                                            {'quantile': 0.95, '_': 12.749999999999995}])

    def test_labels(self):
        metric = getMetric('root.test.FloatValue', 'float')
        metric.runtime(2, label='value')
        metric.runtime(3, label='key')

        self.assertEqual(metric.to_json(), [{'label': 'value', '_': 2}, {'label': 'key', '_': 3}])

    def test_base_metric(self):
        metric = getMetric('root.test.StringValue', 'string')
        metric.runtime('data')

        metric2 = getMetric('root.test.FloatValue', 'float')
        metric2.runtime(2.0)

        metric3 = getMetric('root.test.IntValue', 'int')
        metric3.runtime(3)

        root_metric = getMetric('')

        self.assertEqual(root_metric.to_json(), {
            'root': {
                'test': {
                    'StringValue': {'_': 'data'},
                    'FloatValue': {'_': 2.0},
                    'IntValue': {'_': 3}
                }
            }
        })

    def test_base_metric(self):
        metric2 = getMetric('root.test.FloatValue', 'float', DEBUG)
        metric2.runtime(2.0)
        metric2.debug(1.0)

        metric3 = getMetric('root.test.IntValue', 'int')
        metric3.runtime(3)
        metric3.debug(2)

        root_metric = getMetric('')

        self.assertEqual(root_metric.to_json(), {
            'root': {
                'test': {
                    'FloatValue': {'_': 1.0},
                    'IntValue': {'_': 3}
                }
            }
        })

    def testInheritance(self):
        metric = getMetric('root.test.FloatValue', 'float', INHERIT)
        metric.runtime(2.0)
        metric_parent = getMetric('root.test')

        self.assertEqual(getMetric('').to_json(), {
            'root': {
                'test': {
                    'FloatValue': {'_': 2.0},
                }
            }
        })

        metric_parent.switch_level(RUNTIME)
        metric.debug(3.0)

        self.assertEqual(getMetric('').to_json(), {
            'root': {
                'test': {
                    'FloatValue': {'_': 2.0},
                }
            }
        })

    def test_labels(self):
        metric = getMetric('root.IntValue', 'int', labels={'k': 2})
        metric.runtime(3)
        self.assertEqual(metric.to_json(), {'k': 2, '_': 3})

    def test_cps(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1, 2])
        metric.runtime()
        self.assertEqual([1, 2], metric.time_unit_vectors)
        self.assertEqual([{'period': 1, '_': 1}, {'period': 2, '_': 1}], metric.to_json())
        metric.runtime()
        self.assertEqual([{'period': 1, '_': 2}, {'period': 2, '_': 2}], metric.to_json())
        time.sleep(1.2)
        self.assertEqual([{'period': 1, '_': 0}, {'period': 2, '_': 2}], metric.to_json())
