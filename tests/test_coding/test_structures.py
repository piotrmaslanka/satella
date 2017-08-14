# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding import TimeBasedHeap


class TestTimeBasedHeap(unittest.TestCase):
    def test_tbh(self):

        tbh = TimeBasedHeap()

        tbh.put(10, 'ala')
        tbh.put(20, 'ma')
        tbh.put(30, 'kota')

        q = set(tbh.pop_less_than(25))

        self.assertIn((10, 'ala'), q)
        self.assertIn((20, 'ma'), q)
        self.assertNotIn((30, 'kota'), q)
