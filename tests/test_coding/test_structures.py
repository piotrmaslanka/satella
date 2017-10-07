# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding import TimeBasedHeap, Heap


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


class TestHeap(unittest.TestCase):

    def test_tbh_iter(self):
        tbh = Heap([(10, 'ala'), (20, 'ma'), (30, 'kota'), (5, 'yo')])

        self.assertEqual([(5, 'yo'), (10, 'ala'), (20, 'ma'), (30, 'kota')], list(tbh.iter_ascending()))
        self.assertEqual(reversed([(5, 'yo'), (10, 'ala'), (20, 'ma'), (30, 'kota')]), list(tbh.iter_descending()))

    def test_tbh(self):

        tbh = Heap()

        tbh.push_many([
            (10, 'ala'),
            (20, 'ma')
            ])

        self.assertIn((10, 'ala'), tbh)
        self.assertIn((20, 'ma'), tbh)

        tbh.filtermap(filter_fun=lambda x: x[0] != 20,
                      map_fun=lambda x: (x[0]+10, 'azomg'))

        self.assertIn((20, 'azomg'), tbh)
        self.assertNotIn((10, 'ala'), tbh)
        self.assertNotIn((20, 'ma'), tbh)
