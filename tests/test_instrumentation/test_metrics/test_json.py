import unittest
import typing as tp
import logging
from satella.instrumentation.metrics.json import update

logger = logging.getLogger(__name__)


class TestJson(unittest.TestCase):
    def test_update(self):
        a1 = {'root': {'metric': [{'period': 1, '_': 25.0}, {'period': 2, '_': 50.0}]}}
        a2 = {'root': {'metric': [{'period': 1, '_': 20.0}]}}
        a3 = update(a1, a2)
        logger.warning(a3)
        a4 = {'root': {'metric': [{'period': 1, '_': 20.0}, {'period': 2, '_': 50.0}]}}
        self.assertEqual(a3, a4)
