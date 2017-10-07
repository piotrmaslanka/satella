# coding=UTF-8
from __future__ import print_function, absolute_import, division

import unittest

from satella.coding import TimeBasedHeap, Heap, CallableGroup
import six
import copy


class TestCallableGroup(unittest.TestCase):
    def test_cg_proforma(self):
        cg = CallableGroup()


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

    def test_imprv(self):
        tbh = TimeBasedHeap()
        tbh.put(10, 'ala')

        self.assertIn('ala', list(tbh.items()))


    def test_def(self):

        class DCS(object):
            def __call__(self):
                return self.v
            def set(self, v):
                self.v = v

        clk = DCS()
        clk.set(0)

        tbh = TimeBasedHeap(default_clock_source=clk)
        tbh.put('ala')
        tbh.put(4, 'alla')

        clk.set(3)

        q = set(tbh.pop_less_than())

        self.assertIn((0, 'ala'), q)
        self.assertNotIn((4, 'alla'), q)

    def test_foobar(self):
        tbh = TimeBasedHeap()
        bytes(tbh)
        six.text_type(tbh)
        repr(tbh)
        copy.copy(tbh)
        copy.deepcopy(tbh)


class TestHeap(unittest.TestCase):
    def test_push(self):
        tbh = Heap()
        tbh.push(10, 'A')
        self.assertEquals((10, 'A'), tbh.pop())
        tbh.push((10, 'A'))
        self.assertEquals((10, 'A'), tbh.pop())

    def test_tbh_iter(self):
        tbh = Heap()

        tb = [(10, 'ala'), (20, 'ma'), (30, 'kota'), (5, 'yo')]

        tbh.push_many(tb)
        self.assertEqual(sorted(tb), list(tbh.iter_ascending()))
        self.assertEqual(sorted(tb, reverse=True), list(tbh.iter_descending()))

    def test_tbh(self):
        tbh = Heap()

        tbh.push_many([
            (10, 'ala'),
            (20, 'ma')
        ])

        self.assertIn((10, 'ala'), tbh)
        self.assertIn((20, 'ma'), tbh)

        tbh.filtermap(filter_fun=lambda x: x[0] != 20,
                      map_fun=lambda x: (x[0] + 10, 'azomg'))

        self.assertIn((20, 'azomg'), tbh)
        self.assertNotIn((10, 'ala'), tbh)
        self.assertNotIn((20, 'ma'), tbh)
