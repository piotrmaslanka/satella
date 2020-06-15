import abc
import collections
import copy
import logging
import math
import time
import unittest

import mock

from satella.coding.structures import TimeBasedHeap, Heap, typednamedtuple, \
    OmniHashableMixin, DictObject, apply_dict_object, Immutable, frozendict, SetHeap, \
    DictionaryView, HashableWrapper, TwoWayDictionary, Ranking, SortedList, SliceableDeque, \
    DirtyDict, KeyAwareDefaultDict, Proxy, ReprableMixin, TimeBasedSetHeap, ExpiringEntryDict, SelfCleaningDefaultDict

logger = logging.getLogger(__name__)


class TestMisc(unittest.TestCase):
    def test_expiration_dict_manual_expiring(self):
        eed = ExpiringEntryDict(expiration_timeout=5)
        eed['test'] = 2
        time.sleep(2)
        self.assertEqual(eed['test'], 2)
        time.sleep(4)
        self.assertRaises(KeyError, lambda: eed['test'])

    def test_expiration_dict_self_expiring(self):
        eed = ExpiringEntryDict(expiration_timeout=5, external_cleanup=True)
        eed['test'] = 2
        time.sleep(2)
        self.assertEqual(eed['test'], 2)
        time.sleep(10)
        self.assertRaises(KeyError, lambda: eed.data['test'])

    def test_self_cleaning_default_dict(self):
        sc_dd = SelfCleaningDefaultDict(list)
        sc_dd['test'].append(2)
        sc_dd['test'].pop()
        time.sleep(10)
        self.assertEqual(len(sc_dd), 0)
        sc_dd['test'] = '2'
        self.assertEqual(len(sc_dd), 1)
        del sc_dd['test']
        self.assertEqual(len(sc_dd), 0)

    def test_reprable_mixin(self):
        class Test(ReprableMixin):
            _REPR_FIELDS = ('v',)

            def __init__(self, v):
                self.v = v

        self.assertEqual(repr(Test(2)), 'Test(2)')

        class Test2(ReprableMixin):
            _REPR_FIELDS = ('v',)
            _REPR_FULL_CLASSNAME = True

            def __init__(self, v):
                self.v = v

        self.assertEqual(repr(Test2(2)),
                         'tests.test_coding.test_structures.TestMisc.test_reprable_mixin.<locals>.Test2(2)')

    def test_proxy(self):
        a = Proxy(5, wrap_operations=True)
        self.assertIsInstance(a + 5, Proxy)

        a = Proxy(5)
        self.assertNotIsInstance(a + 5, Proxy)
        self.assertIsInstance(a + 5, int)

        a = Proxy(5.5)
        self.assertEqual(math.floor(a), 5)

    def test_key_aware_defaultdict(self):
        a = KeyAwareDefaultDict(int)
        self.assertEqual(a['1'], 1)

    def test_dirty_dict(self):
        a = DirtyDict({1: 2, 3: 4})
        self.assertFalse(a.dirty)
        a[1] = 3
        self.assertTrue(a.dirty)
        a.clear_dirty()
        self.assertFalse(a.dirty)
        a[1] = 3
        self.assertFalse(a.dirty)
        del a[1]
        self.assertTrue(a.dirty)
        self.assertEqual(a.copy_and_clear_dirty(), {3: 4})
        a[3] = 5
        self.assertTrue(a.dirty)
        self.assertEqual(a.swap_and_clear_dirty(), {3: 5})
        self.assertFalse(a)
        self.assertFalse(a.dirty)

    def test_sliceable_deque(self):
        sd = SliceableDeque([1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(list(sd[1:-1]), [2, 3, 4, 5, 6])
        self.assertEqual(sd.__getitem__(0), 1)

    def test_sorted_list(self):
        sl = SortedList([3, 2, 1], lambda a: a)
        self.assertEqual(sl[0], 1)
        self.assertEqual(sl[-1], 3)
        self.assertEqual(sl.index(2), 1)
        sl.add(5)
        self.assertEqual(sl.index(5), 3)
        self.assertRaises(ValueError, lambda: sl.index(6))
        sl.add(4)
        self.assertEqual(sl.index(5), 4)
        sl.remove(1)
        self.assertEqual(sl.index(5), 3)
        self.assertEqual(sl.pop(), 5)
        self.assertEqual(sl.popleft(), 2)

    def test_two_way_dict2(self):
        self.assertRaises(ValueError, lambda: TwoWayDictionary([(1, 2), (2, 2)]))

    def test_ranking(self):
        Entry = collections.namedtuple('Entry', ('a',))
        e1 = Entry(1)
        e2 = Entry(2)
        e3 = Entry(3)
        ranking = Ranking([e1, e2], lambda e: e.a)  # type: Ranking[Entry]

        self.assertEqual(ranking[0], e1)
        self.assertEqual(ranking[1], e2)
        self.assertEqual(ranking.get_position_of(e1), 0)
        self.assertEqual(list(ranking.get_sorted()), [e1, e2])

        ranking.add(e3)
        self.assertEqual(list(ranking.get_sorted()), [e1, e2, e3])
        ranking.remove(e1)
        self.assertEqual(list(ranking.get_sorted()), [e2, e3])
        self.assertEqual(ranking[-1], e3)
        e25 = Entry(2.5)
        ranking.add(e25)
        self.assertEqual(list(ranking.get_sorted()), [e2, e25, e3])

    def test_two_way_dict(self):
        twd = TwoWayDictionary({1: 2, 3: 4})
        self.assertEqual(twd.reverse[4], 3)
        del twd[1]
        self.assertRaises(KeyError, lambda: twd[1])
        self.assertRaises(KeyError, lambda: twd.reverse[2])
        twd[3] = 8
        self.assertEqual(twd.reverse[8], 3)
        self.assertRaises(KeyError, lambda: twd.reverse[4])

    def test_hashable_wrapper(self):
        class NotHashable:
            def __init__(self, a):
                self.a = a

            def __call__(self, *args, **kwargs):
                return 5

            def __hash__(self):
                raise TypeError()

        nh = NotHashable(5)
        nw = HashableWrapper(nh)
        self.assertEqual(nw.a, 5)
        nw.a = 4
        self.assertEqual(nw.a, 4)
        del nw.a
        self.assertRaises(AttributeError, lambda: getattr(nw, 'a'))
        self.assertEqual(nw, nh)
        self.assertEqual(nw, nw)
        hash(nw)
        self.assertEqual(nw(), 5)

    def test_dictionary_view(self):
        a = {1: 2, 3: 4}
        b = {4: 5, 6: 7}
        dva = DictionaryView(a, b)

        self.assertEqual(dva[1], 2)
        self.assertEqual(dva[4], 5)
        del dva[4]
        self.assertNotIn(4, b)
        self.assertNotIn(4, dva)
        dva[7] = 8
        self.assertIn(7, dva)
        self.assertIn(7, a)
        dva[6] = 10
        self.assertEqual(b[6], 10)

        dvb = DictionaryView(a, b, propagate_deletes=False, assign_to_same_dict=False)
        self.assertRaises(KeyError, lambda: dvb.__delitem__(6))
        dvb[6] = 11
        self.assertEqual(b[6], 10)
        self.assertEqual(a[6], 11)

        self.assertEqual(len(dvb), 4)

    def test_setheap(self):
        a = SetHeap([1, 2, 3])
        self.assertIn(2, a)
        self.assertEqual(1, a.pop())
        self.assertNotIn(1, a)
        a.push_many([3, 4])
        self.assertEqual(len(a), 3)

    def test_frozendict(self):
        a = frozendict({1: 2, 3: 4})
        self.assertEqual(a[1], 2)
        self.assertRaises(TypeError, lambda: a.__setitem__(1, 3))
        b = frozendict({1: 2, 3: 4})
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertRaises(TypeError, lambda: a.update({3: 5}))

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
        self.assertEqual(hash(e1), hash(2))

    def test_tbsh(self):
        tbh = TimeBasedSetHeap()

        tbh.put(10, 'ala')
        tbh.put(20, 'ma')
        tbh.put(30, 'kota')
        tbh.put(30, 'ala')
        self.assertIn((30, 'ala'), tbh)
        self.assertNotIn((10, 'ala'), tbh)

        q = set(tbh.pop_less_than(25))

        self.assertIn((20, 'ma'), q)
        self.assertNotIn((30, 'ala'), q)
        self.assertNotIn((30, 'kota'), q)

        self.assertIsInstance(copy.copy(tbh), TimeBasedSetHeap)
        self.assertIsInstance(copy.deepcopy(tbh), TimeBasedSetHeap)

        item = tbh.pop_timestamp(30)
        self.assertTrue(item == 'kota' or item == 'ala')

    def test_tbh(self):
        tbh = TimeBasedHeap()

        tbh.put(10, 'ala')
        tbh.put(20, 'ma')
        tbh.put(30, 'kota')

        q = set(tbh.pop_less_than(25))

        self.assertIn((10, 'ala'), q)
        self.assertIn((20, 'ma'), q)
        self.assertNotIn((30, 'kota'), q)

        self.assertIsInstance(copy.copy(tbh), TimeBasedHeap)
        self.assertIsInstance(copy.deepcopy(tbh), TimeBasedHeap)

        item = tbh.pop_timestamp(30)
        self.assertEqual(item, 'kota')
        self.assertNotIn((30, 'kota'), tbh)

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

    def test_valid_schema(self):
        self.assertTrue(DictObject({'a': 5, 'b': 'test'}).is_valid_schema({'a': int, 'b': str}))
        self.assertFalse(DictObject({'a': 5, 'b': 'test'}).is_valid_schema({'a': int, 'b': int}))
        self.assertTrue(DictObject({'a': 5, 'b': 'test'}).is_valid_schema(a=int, b=str))
        self.assertFalse(DictObject({'a': 5, 'b': 'test'}).is_valid_schema(a=int, b=int))

    def test_apply_dict_object(self):
        a = {'a': {'b': 5}, 'c': [{'a': 5}]}
        b = DictObject({'a': DictObject({'b': 5}), 'c': [DictObject({'a': 5})]})
        a = apply_dict_object(a)
        self.assertEqual(apply_dict_object(a), b)
        self.assertIsInstance(a, DictObject)
        self.assertIsInstance(a.a, DictObject)
        self.assertIsInstance(a.c[0], DictObject)

    def test_dict_object(self):
        a = {'a': 1, 'b': 2}

        a = DictObject(a)

        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, 2)
        self.assertRaises(AttributeError, lambda: a.c)
        del a.a
        self.assertRaises(AttributeError, lambda: a.a)
        a.a = 5
        self.assertEqual(a.a, 5)

        def delete():
            del a.c

        self.assertRaises(AttributeError, delete)

    def test_copying(self):
        a = DictObject({1: 2})
        b = copy.copy(a)
        self.assertEqual(a, b)
        self.assertFalse(id(a) == id(b))
        c = copy.deepcopy(a)
        c[1] = 3
        self.assertEqual(a[1], 2)
        self.assertEqual(c[1], 3)


class TestHeap(unittest.TestCase):
    def test_push(self):
        tbh = Heap()
        tbh.push(10, 'A')
        self.assertEqual((10, 'A'), tbh.pop())
        tbh.push((10, 'A'))
        self.assertEqual(tbh[0], (10, 'A'))
        self.assertEqual((10, 'A'), tbh.pop())
        self.assertEqual(tbh.data, [])

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

        tbh.filter_map(filter_fun=lambda x: x[0] != 20,
                       map_fun=lambda x: (x[0] + 10, 'test3'))

        self.assertIn((20, 'test3'), tbh)
        self.assertNotIn((10, 'ala'), tbh)
        self.assertNotIn((20, 'ma'), tbh)

        item = tbh.pop_item((20, 'test3'))
        self.assertNotIn((20, 'test3'), tbh)
        self.assertEqual(item, (20, 'test3'))


class TestImmutable(unittest.TestCase):
    def _test_an_instance(self, a):
        self.assertEqual(a.x, 2.5)
        self.assertEqual(a.y, 2)

        def change_x():
            a.x = 2

        self.assertRaises(TypeError, change_x)

        def delete_x():
            del a.x

        self.assertRaises(TypeError, delete_x)

    def test_immutable(self):
        class Point2D(Immutable):
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

        self._test_an_instance(Point2D(2.5, 2))

    def test_immutable_abc(self):
        class Point2D(abc.ABC, Immutable):
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

        self._test_an_instance(Point2D(2.5, 2))

    def test_advanced_inheritance_hierarchy(self):
        class AnObject:
            pass

        class BaseClass(metaclass=abc.ABCMeta):
            pass

        class AnotherBaseClass(metaclass=abc.ABCMeta):
            pass

        class TwinnedBaseClass(AnotherBaseClass, metaclass=abc.ABCMeta):
            pass

        class Point2D:
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

        class Point3D(Point2D, BaseClass, TwinnedBaseClass, AnObject, Immutable):
            pass

        self._test_an_instance(Point3D(2.5, 2))
