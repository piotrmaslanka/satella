import abc
import collections
import copy
import math
import time
import unittest

from unittest import mock

from satella.coding.concurrent import call_in_separate_thread
from satella.coding.structures import TimeBasedHeap, Heap, typednamedtuple, \
    OmniHashableMixin, DictObject, apply_dict_object, Immutable, frozendict, SetHeap, \
    DictionaryView, HashableWrapper, TwoWayDictionary, Ranking, SortedList, SliceableDeque, \
    DirtyDict, KeyAwareDefaultDict, Proxy, ReprableMixin, TimeBasedSetHeap, ExpiringEntryDict, SelfCleaningDefaultDict, \
    CacheDict, StrEqHashableMixin, ComparableIntEnum, HashableIntEnum, ComparableAndHashableBy, \
    ComparableAndHashableByInt, SparseMatrix, ExclusiveWritebackCache, Subqueue, \
    CountingDict, ComparableEnum, LRU, LRUCacheDict, Vector, DefaultDict, PushIterable, \
    ComparableAndHashableByStr


class TestMisc(unittest.TestCase):

    def test_push_iterable(self):

        a = PushIterable([1, 2, 3])
        self.assertEqual(a.pop(), 1)
        a.push(0)
        self.assertEqual(a.pop(), 0)
        self.assertEqual(a.pop(), 2)
        a.push(0)
        a.push(1)
        self.assertEqual(a.pop(), 1)
        self.assertEqual(a.pop(), 0)
        a.push_left(0)
        a.push_left(1)
        self.assertEqual(a.pop(), 0)
        self.assertEqual(a.pop(), 1)
        self.assertEqual(a.pop(), 3)
        self.assertRaises(StopIteration, a.pop)

    def test_default_dict(self):
        a = DefaultDict(lambda: '')
        a[2]
        self.assertNotIn(2, a)

    def test_vector(self):
        a = Vector((2, 3))
        self.assertEqual(a-Vector((1, 2)), Vector((1, 1)))
        self.assertEqual(a*2, Vector((4, 6)))
        self.assertEqual(a/2, Vector((1, 1.5)))

    def test_lru_cache_dict(self):
        class TestCacheGetter:
            def __init__(self):
                self.called_on = {}
                self.value = 2

            def __call__(self, key):
                if self.value is None:
                    raise KeyError('no value available')
                self.called_on[key] = time.monotonic()
                return self.value

        cg = TestCacheGetter()
        cd = LRUCacheDict(1, 2, cg, max_size=3)

        self.assertEqual(cd[1], 2)
        self.assertEqual(cd[2], 2)
        self.assertEqual(cd[3], 2)
        self.assertEqual(cd[4], 2)
        self.assertEqual(len(cd), 3)

    def test_lru(self):
        lru = LRU()
        lru.add('a')
        lru.add('b')
        lru.add('c')
        self.assertEqual(lru.get_item_to_evict(), 'a')
        lru.mark_as_used('b')
        self.assertEqual(lru.get_item_to_evict(), 'c')
        self.assertEqual(len(lru), 1)

    def test_comparable_enum(self):
        class MyEnum(ComparableEnum):
            A = 'test'
            B = 'test2'

        self.assertEqual(MyEnum.A, 'test')
        self.assertNotEqual(MyEnum.B, 'test')

    def test_counting_dict(self):
        cd = CountingDict([1, 1, 2, 2, 3])
        self.assertEqual(cd[1], 2)
        self.assertEqual(list(cd), [1, 2, 3])
        cd.clear()
        self.assertFalse(cd)

    def test_subqueue(self):
        a = Subqueue()
        a.put('test', 2)
        self.assertEqual(a.get('test'), 2)

        @call_in_separate_thread()
        def put_a_message():
            nonlocal a
            time.sleep(1)
            a.put('test', 5)

        put_a_message()
        self.assertEqual(a.get('test'), 5)
        a.put('test2', 4)
        self.assertEqual(a.qsize(), 1)
        self.assertEqual(a.get_any(), ('test2', 4))

    def test_exclusive_writeback_cache(self):
        a = {5: 3, 4: 2, 1: 0}
        b = {'no_calls': 0}

        def setitem(k, v):
            nonlocal a, b
            b['no_calls'] += 1
            a[k] = v

        def getitem(k):
            nonlocal a, b
            b['no_calls'] += 1
            return a[k]

        def delitem(k):
            nonlocal a, b
            b['no_calls'] += 1
            del a[k]

        wbc = ExclusiveWritebackCache(setitem, getitem, delitem)
        self.assertEqual(wbc[5], 3)
        self.assertEqual(b['no_calls'], 1)
        self.assertRaises(KeyError, lambda: wbc[-1])
        self.assertEqual(b['no_calls'], 2)
        self.assertEqual(wbc[5], 3)
        self.assertEqual(b['no_calls'], 2)
        wbc[5] = 2
        wbc.sync()
        self.assertEqual(a[5], 2)
        self.assertEqual(b['no_calls'], 3)
        del wbc[4]
        wbc.sync()
        self.assertRaises(KeyError, lambda: a[4])

    def test_sparse_matrix(self):
        sm = SparseMatrix()
        sm[1, 2] = 1
        sm[0, 0] = 2
        self.assertEqual(list(sm), [[2, None], [None, None], [None, 1]])
        self.assertEqual(sm.columns, 2)
        self.assertEqual(sm.rows, 3)
        sm[1, 2] = 3
        self.assertEqual(list(sm), [[2, None], [None, None], [None, 3]])
        del sm[1, 2]
        a = list(sm)
        self.assertEqual(a, [[2]])
        sm[:, 2] = [5, 6, 7]
        self.assertEqual(list(sm), [[2, None, None], [None, None, None], [5, 6, 7]])
        sm[1, :] = [1, 2, 3]
        self.assertEqual(sm[1, :], [1, 2, 3])
        self.assertEqual(sm[:, 1], [None, 2, None])
        self.assertEqual(list(sm), [[2, 1, None], [None, 2, None], [5, 3, 7]])
        del sm[1, 2]
        self.assertEqual(list(sm), [[2, 1, None], [None, 2, None], [5, None, 7]])
        self.assertEqual(sm[-1, -1], 7)
        sm2 = SparseMatrix.from_iterable([[2, 1, None], [None, 2, None], [5, None, 7]])
        self.assertEqual(sm, sm2)
        del sm[1, :]
        self.assertEqual(list(sm), [[2, None, None], [None, None, None], [5, None, 7]])
        del sm[:, 2]
        self.assertEqual(list(sm), [[2]])
        del sm[:, :]
        self.assertEqual(list(sm), [])
        sm.append_row([1, 2])
        self.assertEqual(list(sm), [[1, 2]])
        sm = SparseMatrix([[1, 2], [3, 4]])
        self.assertEqual(list(sm), [[1, 2], [3, 4]])
        sm2 = sm.shoot()
        self.assertEqual(list(sm2), [[1, None, 2], [None, None, None], [3, None, 4]])
        self.assertEqual(set(sm2.get_neighbour_coordinates(0, 0)), {(0, 1), (1, 0), (1, 1)})
        self.assertEqual(set(sm2.get_neighbour_coordinates(1, 1, False)), {(0, 1), (1, 0), (2, 1), (1, 2)})
        self.assertEqual(set(sm2.get_neighbour_coordinates(2, 2)), {(2, 1), (1, 1), (1, 2)})
        self.assertEqual(sm2.min(), 1)
        self.assertEqual(sm2.max(), 4)
        self.assertRaises(IndexError, lambda: sm2[3, 3])

    def test_comparable_and_hashable_by_int(self):
        class MyClass(ComparableAndHashableByInt):
            def __init__(self, a: int):
                self.a = a

            def __int__(self):
                return self.a

        a = MyClass(1)
        b = MyClass(1)
        c = MyClass(2)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertLess(a, c)
        self.assertGreaterEqual(a, b)
        self.assertGreaterEqual(c, b)
        self.assertEqual(hash(a), hash(b))

    def test_comparable_and_hashable_by(self):
        class Vector(ComparableAndHashableBy):
            _COMPARABLE_BY = 'a'

            def __init__(self, a):
                self.a = a

        self.assertTrue(Vector(1) < Vector(2))
        self.assertTrue(Vector(1) <= Vector(2))
        self.assertFalse(Vector(1) > Vector(2))
        self.assertFalse(Vector(1) >= Vector(2))
        self.assertFalse(Vector(1) == Vector(2))
        self.assertEqual(hash(Vector(1)), hash(1))

    def test_comparable_and_hashable_by_str(self):
        class Vector(ComparableAndHashableByStr):

            def __str__(self) -> str:
                return self.a

            def __init__(self, a):
                self.a = a

        self.assertTrue(Vector('a') < Vector('ab'))
        self.assertTrue(Vector('a') <= Vector('a'))
        self.assertFalse(Vector('a') > Vector('b'))
        self.assertFalse(Vector('a') >= Vector('b'))
        self.assertFalse(Vector('a') == Vector('b'))
        self.assertEqual(hash(Vector('a')), hash('a'))

    def test_hashable_int_enum(self):
        class A(HashableIntEnum):
            A = 0
            B = 1

        self.assertEqual({A.A: 't', A.B: 'c'}[A.A], 't')

    def test_comparable_enum(self):
        class A(ComparableEnum):
            A = 1

        class B(ComparableEnum):
            A = 1

        self.assertEqual(A.A, B.A)

    def test_comparable_int_enum_bug1(self):
        def test_comparable_int_enum(self):
            A = 0
            B = 1
            C = 2
            class Enum(ComparableIntEnum):
                A = A
                B = B
                C = C

            self.assertTrue(Enum.A < B)
            self.assertTrue(Enum.A <= B)
            self.assertTrue(Enum.A <= A)
            self.assertFalse(Enum.A > B)
            self.assertFalse(Enum.A >= B)
            self.assertFalse(Enum.A == B)
            self.assertEqual({Enum.A: 't'}[A], 't')

    def test_comparable_int_enum(self):

        class Enum(ComparableIntEnum):
            A = 0
            B = 1
            C = 2

        self.assertTrue(Enum.A < Enum.B)
        self.assertTrue(Enum.A <= Enum.B)
        self.assertTrue(Enum.A <= Enum.A)
        self.assertFalse(Enum.A > Enum.B)
        self.assertFalse(Enum.A >= Enum.B)
        self.assertFalse(Enum.A == Enum.B)
        self.assertEqual({Enum.A: 't'}[Enum.A], 't')

    def test_str_eq_hashable_mixin(self):
        class MyClass(StrEqHashableMixin):
            def __init__(self, v: str):
                self.v = v

            def __str__(self) -> str:
                return self.v

        a = MyClass('a')
        self.assertEqual(hash('a'), hash(a))
        self.assertEqual(a, 'a')

    def test_proxy(self):
        a = Proxy(2)
        self.assertEqual(int(a), 2)
        self.assertEqual(a, 2)
        self.assertEqual(a+2, 4)
        self.assertEqual(a*2, 4)
        self.assertEqual(a-2, 0)
        self.assertIsNotNone(hash(a))
        self.assertIsNotNone(repr(a))
        self.assertEqual(str(a), '2')
        self.assertEqual(abs(a), 2)
        self.assertEqual(a/2, 1)
        self.assertEqual(a//2, 1)
        a += 1
        self.assertEqual(a, 3)
        a -= 1
        self.assertEqual(a, 2)
        a *= 2
        self.assertEqual(a, 4)
        a /= 2
        self.assertEqual(a, 1.0)
        a = Proxy(2)
        a //= 2
        self.assertEqual(a, 1)
        a <<= 1
        self.assertEqual(a, 2)
        a >>= 1
        self.assertEqual(a, 1)
        a ^= 1
        self.assertEqual(a, 0)
        self.assertEqual(a ^ 2, 2)
        a = Proxy(2)
        self.assertEqual(a << 1, 4)
        self.assertEqual(a >> 1, 1)
        a = Proxy(2)
        self.assertEqual(a ** 2, 4)
        a **= 2
        self.assertEqual(a, 4)
        self.assertEqual(-a, 4)
        self.assertEqual(+a, 4)
        self.assertTrue(a > 1)
        self.assertFalse(a < 1)
        self.assertTrue(a >= 1)
        self.assertFalse(a <= 1)

        b = Proxy(list)
        self.assertEqual(b((1, 2, 3)), [1, 2, 3])
        self.assertIsNotNone(b.insert)

        c = Proxy([1, 2, 3])
        self.assertEqual(len(c), 3)
        self.assertEqual(list(iter(c)), [1, 2, 3])
        self.assertEqual(c[0], 1)
        del c[0]
        self.assertEqual(c, [2, 3])
        c.append(4)
        self.assertEqual(c, [2, 3, 4])
        self.assertIn(2, c)

    def test_cache_dict(self):
        class TestCacheGetter:
            def __init__(self):
                self.called_on = {}
                self.value = 2

            def __call__(self, key):
                if self.value is None:
                    raise KeyError('no value available')
                self.called_on[key] = time.monotonic()
                return self.value

        cg = TestCacheGetter()
        cd = CacheDict(1, 2, cg)
        now = time.monotonic()
        self.assertEqual(cd[2], 2)
        self.assertEqual(list(cd), [2])
        self.assertGreaterEqual(cg.called_on[2], now)
        time.sleep(0.2)
        now = time.monotonic()
        self.assertLessEqual(cg.called_on[2], now)
        time.sleep(0.9)
        now = time.monotonic()
        self.assertEqual(cd[2], 2)
        time.sleep(0.2)
        self.assertGreaterEqual(cg.called_on[2], now)
        self.assertEqual(cd[2], 2)
        time.sleep(2.9)
        cg.value = 3
        now = time.monotonic()
        self.assertEqual(cd[2], 3)
        self.assertGreaterEqual(cg.called_on[2], now)
        del cd[2]
        self.assertEqual(len(cd), 0)
        cg.value = None
        self.assertRaises(KeyError, lambda: cd[2])
        cg.value = 2
        self.assertEqual(cd[2], 2)
        cg.value = None
        time.sleep(1.5)
        self.assertEqual(cd[2], 2)
        time.sleep(0.6)
        self.assertRaises(KeyError, lambda: cd[2])

        cd = CacheDict(1, 2, cg, cache_failures_interval=1)
        self.assertRaises(KeyError, lambda: cd[2])
        cg.value = 2
        self.assertRaises(KeyError, lambda: cd[2])
        time.sleep(1.1)
        self.assertEqual(cd[2], 2)
        cd.feed(5, 6)
        self.assertEqual(cd[5], 6)

    def test_cache_dict_default_value_factory(self):
        class TestCacheGetter:
            def __call__(self, key):
                raise KeyError('no value available')

        cg = TestCacheGetter()
        cd = CacheDict(1, 2, cg, cache_failures_interval=1, default_value_factory=list)
        self.assertEqual(cd[2], [])
        self.assertEqual(cd[2], [])

    def test_dictobject_dictobject(self):
        a = DictObject(a=5, k=3)
        b = DictObject(a)
        b.c = 4
        self.assertEqual(b.a, 5)
        self.assertEqual(b.k, 3)
        self.assertEqual(b.c, 4)

        self.assertIn('DictObject', str(b))
        self.assertIn('DictObject', repr(b))
        self.assertIn('a', b.keys())
        self.assertIn(5, b.values())
        self.assertIn(('a', 5), b.items())

    def test_dictobject_setdefault(self):
        a = DictObject()
        self.assertEqual(a.setdefault('k', 2), 2)
        self.assertEqual(a.k, 2)

        self.assertIsNone(a.get('v'))
        self.assertEqual(a.get('k'), 2)
        self.assertIn('k', a)

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

    def test_self_cleaning_default_dict_no_background_maintenance(self):
        sc_dd = SelfCleaningDefaultDict(list, False)
        sc_dd['test'].append(2)
        sc_dd['test'].pop()
        sc_dd['test'] = '2'
        self.assertEqual(len(sc_dd), 1)
        del sc_dd['test']
        self.assertEqual(len(sc_dd), 0)

    def test_self_cleaning_default_dict_background_maintenance(self):
        sc_dd = SelfCleaningDefaultDict(list)
        sc_dd['test'] = [1]
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

        self.assertTrue(repr(Test2(2)).endswith(
            'test_coding.test_structures.TestMisc.test_reprable_mixin.<locals>.Test2(2)'))

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

    def test_set_heap(self):
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

    def continue_testing_omni(self, Omni):
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

    def test_omni_single_field(self):
        class Omni(OmniHashableMixin):
            _HASH_FIELDS_TO_USE = 'a'

            def __init__(self, a):
                self.a = a

        self.continue_testing_omni(Omni)

    def test_omni(self):
        class Omni(OmniHashableMixin):
            _HASH_FIELDS_TO_USE = ('a', )

            def __init__(self, a):
                self.a = a
        self.continue_testing_omni(Omni)

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

        self.assertEqual(tbh.peek_closest(), (10, 'ala'))

        q = set(tbh.pop_less_than(25))

        self.assertIn((10, 'ala'), q)
        self.assertIn((20, 'ma'), q)
        self.assertNotIn((30, 'kota'), q)

        self.assertIsInstance(copy.copy(tbh), TimeBasedHeap)
        self.assertIsInstance(copy.deepcopy(tbh), TimeBasedHeap)

        item = tbh.pop_timestamp(30)
        self.assertEqual(item, 'kota')
        self.assertNotIn((30, 'kota'), tbh)

    def test_improve(self):
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

    def test_constructor(self):
        a = DictObject({'a': 5})
        b = apply_dict_object(a)
        self.assertIs(a, b)

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
