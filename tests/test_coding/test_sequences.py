import logging
import unittest

from satella.coding.sequences import choose, infinite_counter, take_n, is_instance

logger = logging.getLogger(__name__)


class TestSequences(unittest.TestCase):

    def test_take_n(self):
        subset = take_n(infinite_counter(), 10)
        for a, b in zip(range(10), subset):
            self.assertEqual(a, b)

    def test_infinite_counter(self):
        p = infinite_counter(1)
        for i in range(1, 10):
            a = next(p)
            self.assertEqual(a, i)

    def test_choose(self):
        self.assertEqual(choose(lambda x: x == 2, [1, 2, 3, 4, 5]), 2)
        self.assertRaises(ValueError, lambda: choose(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
        self.assertRaises(ValueError, lambda: choose(lambda x: x == 0, [1, 2, 3, 4, 5]))

    def test_is_instance(self):
        objects = [object(), object(), [], [], object()]
        self.assertEqual(len(list(filter(is_instance(list), objects))), 2)
