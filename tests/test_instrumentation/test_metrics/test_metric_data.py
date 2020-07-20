import logging
import unittest

from satella.instrumentation.metrics.data import MetricData, MetricDataCollection

logger = logging.getLogger(__name__)


class TestMetricData(unittest.TestCase):

    def test_internal(self):
        md = MetricData('name', 2, {'labels': 'key'}, None, True)
        md2 = MetricData.from_json(md.to_json())
        self.assertTrue(md2.internal)

    def test_metric_data_collection_add(self):
        a = MetricDataCollection(MetricData('root', 3, {'labels': 'key'}),
                                 MetricData('root_a', 3, {'labels': 'key'}))
        a += MetricDataCollection(MetricData('root', 2, {'labels': 'key'}),
                                  MetricData('root_a', 4, {'labels': 'key'}))

    def test_update_labels_2(self):
        a = MetricDataCollection(MetricData('root', 2, {'labels': 'key'}))
        a.add_labels({'service': 'wtf'})
        self.assertEqual(next(iter(a.values)).labels, {'labels': 'key', 'service': 'wtf'})

    def test_json_serialization(self):
        a = MetricDataCollection(MetricData('root', 2, {'labels': 'key'}))
        b = a.to_json()
        self.assertTrue(a.strict_eq(MetricDataCollection.from_json(b)))

    def test_update_labels(self):
        a = MetricData('root', 2, {'labels': 'key'})
        a.add_labels({'service': 'wtf'})
        self.assertEqual(a.labels, {'labels': 'key', 'service': 'wtf'})

    def test_update_3(self):
        a1 = MetricDataCollection(MetricData('root.metric', 2, {'service': 'my_service'}))
        a1 += MetricData('root.metric', 10, {'service': 'my_service'}, 10)
        self.assertTrue(MetricDataCollection(
            MetricData('root.metric', 10, {'service': 'my_service'}, 10)).strict_eq(a1))

    def test_update_4(self):
        a1 = MetricDataCollection(
            MetricData('root.metric', 2, {'service': 'my_service', 'slot': 1}))
        a1 += MetricDataCollection(
            MetricData('root.metric', 10, {'service': 'my_service', 'slot': 1}, 10))
        self.assertTrue(MetricDataCollection(
            MetricData('root.metric', 10, {'service': 'my_service', 'slot': 1}, 10)).strict_eq(a1))

    def test_update(self):
        a1 = MetricDataCollection(MetricData('root.metric', 25.0, {'period': 1}),
                                  MetricData('root.metric', 50.0, {'period': 2}))
        a2 = MetricDataCollection(MetricData('root.metric', 20.0, {'period': 1}))
        a3 = a1 + a2
        self.assertTrue(MetricDataCollection(MetricData('root.metric', 20.0, {'period': 1}),
                                             MetricData('root.metric', 50.0,
                                                        {'period': 2})).strict_eq(a3))

    def test_postfix_and_prefix(self):
        a = MetricDataCollection(MetricData('root', 3))
        a.prefix_with('test')
        self.assertTrue(MetricDataCollection(MetricData('test.root', 3)).strict_eq(a))

        a = MetricDataCollection(MetricData('root', 3))
        a.postfix_with('test')
        self.assertTrue(MetricDataCollection(MetricData('root.test', 3)).strict_eq(a))

    def test_update_2(self):
        a = MetricDataCollection(MetricData('root', 3, {'a': 5}),
                                 MetricData('root.sum', 3, {'a': 5}))
        b = MetricDataCollection(MetricData('root', 7, {'a': 5}),
                                 MetricData('root.sum', 8, {'a': 3}))
        a += b
        self.assertTrue(MetricDataCollection(MetricData('root', 7, {'a': 5}),
                                             MetricData('root.sum', 8, {'a': 3}),
                                             MetricData('root.sum', 3, {'a': 5})).strict_eq(a))
