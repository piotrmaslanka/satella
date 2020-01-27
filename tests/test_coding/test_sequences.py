import logging
import typing as tp
import unittest

from satella.coding.sequences import choose

logger = logging.getLogger(__name__)


class TestSequences(unittest.TestCase):
    def test_choose(self):
        self.assertEqual(choose(lambda x: x == 2, [1, 2, 3, 4, 5]), 2)
        self.assertRaises(ValueError, lambda: choose(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
        self.assertRaises(ValueError, lambda: choose(lambda x: x == 0, [1, 2, 3, 4, 5]))
