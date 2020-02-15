import logging
import time
import unittest

import requests

from satella.instrumentation.metrics import MetricData, MetricDataCollection
from satella.instrumentation.metrics import getMetric
from satella.instrumentation.metrics.exporters import metric_data_collection_to_prometheus, \
    PrometheusHTTPExporterThread

logger = logging.getLogger(__name__)


class TestExporters(unittest.TestCase):
    def test_prometheus_timestamps(self):
        a = MetricDataCollection(MetricData('root', 5, timestamp=10))
        self.assertEqual("""root 5 10000\n""", metric_data_collection_to_prometheus(a))

    def test_internal_metrics(self):
        metric = getMetric('internal_metric', 'int', internal=True)
        metric.runtime(2)
        self.assertNotIn('internal_metric', metric_data_collection_to_prometheus(
            getMetric('').to_metric_data()))

    def test_prometheus(self):
        a = MetricDataCollection([MetricData('root.metric', 3, {'k': 2, 'm': '"'}),
                                  MetricData('root.metric', 6, {'k': 4})])
        b = metric_data_collection_to_prometheus(a)
        self.assertIn("""root_metric{k="4"} 6""", b)

    def test_exporter_http_server(self):
        with PrometheusHTTPExporterThread('localhost', 1025):
            metr = getMetric('test.metric', 'int')
            metr.runtime(5)
            time.sleep(0.5)
            data = requests.get('http://localhost:1025/metrics')
            self.assertEqual(200, data.status_code)
            self.assertIn('test_metric 5', data.text)
            data2 = requests.get('http://localhost:1025/404')
            self.assertEqual(404, data2.status_code)
