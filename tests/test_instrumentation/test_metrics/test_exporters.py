import unittest
import typing as tp
import logging
from satella.instrumentation.metrics.exporters import json_to_prometheus

logger = logging.getLogger(__name__)


class TestExporters(unittest.TestCase):
    def test_prometheus(self):

        a = {'root': {'metric': [{'k': 2, '_': 3, 'm': '"'}, {'k': 4, '_': 6}]}}
        b = json_to_prometheus(a)
        logger.warning(b)
        self.assertTrue(b == """root_metric{k=2,m="\\""} 3
root_metric{k=4} 6
""".replace('\r\n', '\n') or b == """root_metric{m="\\"",k=2} 3
root_metric{k=4} 6
""".replace('\r\n', '\n'))

    def test_prometheus_2(self):
        a = {'root': {'_': [{'k': 2, '_': 3}], 'sum': {'_': 4}}}
        b = json_to_prometheus(a)
        self.assertEqual("""root{k=2} 3
root_sum 4
""".replace('\r\n', '\n'), b)
