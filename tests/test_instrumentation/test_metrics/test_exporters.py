import unittest
import typing as tp
from satella.instrumentation.metrics.exporters import json_to_prometheus


class TestExporters(unittest.TestCase):
    def test_prometheus(self):

        a = {'root': {'metric': [{'k': 2, '_': 3, 'm': '"'}, {'k': 4, '_': 6}]}}
        b = json_to_prometheus(a)
        self.assertTrue(b == """root_metric{k=2, m="\""} 3
root_metric{k=4} 6
""" or b == """root_metric{m="\"", k=2} 3
root_metric{k=4} 6
""")

