import logging
import unittest

from satella.coding.sequences import n_th
from satella.instrumentation.metrics.data import MetricData, MetricDataCollection, MetricDataContainer

logger = logging.getLogger(__name__)

def mk_metric_data_collection(*metric_data: MetricData):
    return MetricDataCollection([MetricDataContainer('', metric_data)])


class TestMetricData(unittest.TestCase):

    def test_contains(self):
        a = MetricDataContainer('', [MetricData('root', 2, {})])
        self.assertIn(MetricData('root', 4, {}), a.entries)

    def test_equal(self):
        a = MetricData('root', 2, {})
        b = MetricData('root', 3, {})
        self.assertEqual(a, b)

    def test_update_labels_2(self):
        a = MetricDataCollection([MetricDataContainer('', [MetricData('root', 2, {'labels': 'key'})])])
        a.add_labels({'service': 'wtf'})
        self.assertEqual(n_th(n_th(a.values)).labels, {'labels': 'key', 'service': 'wtf'})

    def test_json_serialization(self):
        a = MetricDataCollection([MetricDataContainer('', [MetricData('root', 2, {'labels': 'key'})])])
        b = a.to_json()
        self.assertTrue(a.strict_eq(MetricDataCollection.from_json(b)))

    def test_update_labels(self):
        a = MetricData('root', 2, {'labels': 'key'})
        a.add_labels({'service': 'wtf'})
        self.assertEqual(a.labels, {'labels': 'key', 'service': 'wtf'})

    def test_update_3(self):
        a1 = mk_metric_data_collection(MetricData('root.metric', 2, {'service': 'my_service'}))
        a1 += MetricDataContainer('', [MetricData('root.metric', 10, {'service': 'my_service'})])
        self.assertTrue(mk_metric_data_collection(
            MetricData('root.metric', 10, {'service': 'my_service'})).strict_eq(a1))

    def test_postfix_and_prefix(self):
        a = MetricDataCollection([MetricDataContainer('', [MetricData('root', 3)])])
        a.prefix_with('test')
        self.assertTrue(MetricDataCollection([MetricDataContainer('', [MetricData('test.root', 3)])]).strict_eq(a))

        a = MetricDataCollection([MetricDataContainer('', [MetricData('root', 3)])])
        a.postfix_with('test')
        self.assertTrue(mk_metric_data_collection(MetricData('root.test', 3)).strict_eq(a))

    def test_update_2(self):
        a = mk_metric_data_collection(MetricData('root', 3, {'a': 5}), MetricData('root.sum', 3, {'a': 5}))
        b = mk_metric_data_collection(MetricData('root', 7, {'a': 5}), MetricData('root.sum', 8, {'a': 5}))
        a += b
        self.assertTrue(b.strict_eq(a))
