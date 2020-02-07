import unittest
import typing as tp
import logging
import requests
from satella.instrumentation.metrics import getMetric
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus, \
    PrometheusHTTPExporterThread
from satella.instrumentation.metrics import MetricData, MetricDataCollection
logger = logging.getLogger(__name__)


class TestExporters(unittest.TestCase):
    def test_prometheus_timestamps(self):
        a = MetricDataCollection(MetricData('root', 5, timestamp=10))
        self.assertEqual("""root 5 10000\n""", metric_data_collection_to_prometheus(a))

    def test_prometheus(self):
        a = MetricDataCollection([MetricData('root.metric', 3, {'k': 2, 'm': '"'}),
                                  MetricData('root.metric', 6, {'k': 4})])
        b = metric_data_collection_to_prometheus(a)
        self.assertIn("""root_metric{k="4"} 6""", b)

    def test_exporter_http_server(self):
        phet = PrometheusHTTPExporterThread('localhost', 1025)
        phet.start()
        metr = getMetric('test.metric', 'int')
        metr.runtime(5)
        data = requests.get('http://localhost:1025/metrics')
        self.assertIn('test_metric 5', data.text)
