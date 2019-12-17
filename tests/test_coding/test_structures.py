# coding=UTF-8
from __future__ import print_function, absolute_import, division

import copy
import unittest

import mock

from satella.coding import TimeBasedHeap, Heap, CallableGroup, typednamedtuple, \
    OmniHashableMixin, DictObject, apply_dict_object


class TestCallableGroup(unittest.TestCase):
    def test_cg_proforma(self):
        cg = CallableGroup()


class TestTimeBasedHeap(unittest.TestCase):
    def test_omni(self):
        class Omni(OmniHashableMixin):
            _HASH_FIELDS_TO_USE = ['a']

            def __init__(self, a):
                self.a = a

        e1 = Omni(2)
        e2 = Omni(1)
        e3 = Omni(1)

        self.assertEqual(e2, e3)
        self.assertNotEqual(e1, e2)
        self.assertNotEqual(e1, e3)

        a = {
            e1: '1', e2: '2', e3: '3'
        }

        self.assertEqual(a[e1], '1')

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

    def test_typednamedtuple(self):
        tnt = typednamedtuple('tnt',
                              ('x', float),
                              ('y', float))

        a = tnt('2.5', y=3)

        self.assertEqual(a.x, 2.5)
        self.assertEqual(a.y, 3.0)
        self.assertIsInstance(a.y, float)
        self.assertIsInstance(a, tuple)

    def test_def(self):
        clk = mock.Mock(return_value=0)

        tbh = TimeBasedHeap(default_clock_source=clk)
        tbh.put('ala')
        tbh.put(4, 'alla')

        clk.return_value = 3

        q = set(tbh.pop_less_than())

        self.assertIn((0, 'ala'), q)
        self.assertNotIn((4, 'alla'), q)

    def test_foobar(self):
        tbh = TimeBasedHeap()
        bytes(tbh)
        str(tbh)
        repr(tbh)
        copy.copy(tbh)
        copy.deepcopy(tbh)


class TestDictObject(unittest.TestCase):
    def test_apply_dict_object(self):
        a = {'a': {'b': 5}, 'c': [{'a': 5}]}
        b = DictObject({'a': DictObject({'b': 5}), 'c': [DictObject({'a': 5})]})
        a = apply_dict_object(a)
        self.assertEquals(apply_dict_object(a), b)
        self.assertIsInstance(a, DictObject)
        self.assertIsInstance(a.a, DictObject)
        self.assertIsInstance(a.c[0], DictObject)

    def test_dict_object(self):
        a = {'a': 1, 'b': 2}

        a = DictObject(a)

        self.assertEquals(a.a, 1)
        self.assertEquals(a.b, 2)
        self.assertRaises(AttributeError, lambda: a.c)
        del a.a
        self.assertRaises(AttributeError, lambda: a.a)
        a.a = 5
        self.assertEquals(a.a, 5)

        def delete():
            del a.c

        self.assertRaises(AttributeError, delete)


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
