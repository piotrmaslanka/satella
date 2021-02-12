import unittest

from satella.coding.optionals import call_if_nnone, iterate_if_nnone, Optional


class TestOptionals(unittest.TestCase):

    def test_optional(self):
        b = Optional(None)
        self.assertFalse(b.consumer.cancel().result())

    def test_iterate(self):
        b = list(iterate_if_nnone([1, 2, 3]))
        c = list(iterate_if_nnone(None))
        self.assertFalse(c)
        self.assertTrue(b)

    def test_optional(self):
        self.assertIsNone(call_if_nnone(None))
        b = call_if_nnone(lambda y: y, 5)
        self.assertIsNotNone(b)
        self.assertEqual(5, b)
