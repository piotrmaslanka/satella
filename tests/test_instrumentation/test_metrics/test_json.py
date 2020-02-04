import unittest
import typing as tp
import logging
from satella.instrumentation.metrics.json import update, annotate_every_leaf_node_with_labels

logger = logging.getLogger(__name__)


class TestJson(unittest.TestCase):
    def test_update(self):
        a1 = {'root': {'metric': [{'period': 1, '_': 25.0}, {'period': 2, '_': 50.0}]}}
        a2 = {'root': {'metric': [{'period': 1, '_': 20.0}]}}
        a3 = update(a1, a2)
        logger.warning(a3)
        a4 = {'root': {'metric': [{'period': 1, '_': 20.0}, {'period': 2, '_': 50.0}]}}
        self.assertEqual(a3, a4)

    def test_annotate(self):
        a = {'root': {'metric': [{'period': 1, '_': 25.0}, {'period': 2, '_': 50.0}]}}
        b = annotate_every_leaf_node_with_labels(a, {'key': 'value'})
        self.assertEqual({'root': {'metric': [{'period': 1, '_': 25.0,
                                               'key': 'value'}, {'period': 2, '_': 50.0,
                                                                 'key': 'value'}]}}, b)
