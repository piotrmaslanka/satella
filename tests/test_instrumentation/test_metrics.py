import unittest
import time
import typing as tp
from satella.instrumentation.metrics import getMetric, DEBUG, RUNTIME, INHERIT


class TestMetric(unittest.TestCase):

    def tearDown(self):
        getMetric('').reset()

    def test_base_metric(self):
        metric = getMetric('root.test.StringValue', 'string')
        metric.runtime('data')

        metric2 = getMetric('root.test.FloatValue', 'float')
        metric2.runtime(2.0)

        metric3 = getMetric('root.test.IntValue', 'int')
        metric3.runtime(3)

        root_metric = getMetric('')

        self.assertEquals(root_metric.to_json(), {
            'root': {
                'test': {
                    'StringValue': 'data',
                    'FloatValue': 2.0,
                    'IntValue': 3
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

        self.assertEquals(root_metric.to_json(), {
            'root': {
                'test': {
                    'FloatValue': 1.0,
                    'IntValue': 3
                }
            }
        })

    def testInheritance(self):
        metric = getMetric('root.test.FloatValue', 'float', INHERIT)
        metric.runtime(2.0)
        metric_parent = getMetric('root.test')

        self.assertEquals(getMetric('').to_json(), {
            'root': {
                'test': {
                    'FloatValue': 2.0,
                }
            }
        })

        metric_parent.switch_level(RUNTIME)
        metric.debug(3.0)

        self.assertEquals(getMetric('').to_json(), {
            'root': {
                'test': {
                    'FloatValue': 2.0,
                }
            }
        })

    def test_cps(self):
        metric = getMetric('root.CPSValue', 'cps', time_unit_vectors=[1, 2])
        metric.runtime()
        self.assertEquals(metric.to_json(), [1])
        metric.runtime()
        self.assertEquals(metric.to_json(), [2])
        time.sleep(1.2)
        self.assertEquals(metric.to_json(), [0])

