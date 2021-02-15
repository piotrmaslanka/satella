import itertools
import unittest

from satella.coding.sequences import choose, choose_one, infinite_counter, take_n, is_instance, \
    is_last, add_next, half_cartesian, skip_first, zip_shifted, stop_after, group_quantity, \
    iter_dict_of_list, shift, other_sequence_no_longer_than, count, even, odd, Multirun, n_th, \
    unique, length, map_list, smart_zip, is_empty, make_list, RollingArithmeticAverage, \
    enumerate2, infinite_iterator, to_iterator, filter_out_false, filter_out_nones, \
    index_of, index_of_max, try_close, f_range, iterate_callable, AlreadySeen, \
    append_sequence
from satella.coding.predicates import x


class TestSequences(unittest.TestCase):

    def test_append_sequence(self):
        a = [(1,), (2,), (3,)]
        self.assertEqual(list(append_sequence(a, 1, 2)), [(1, 1, 2), (2, 1, 2), (3, 1, 2)])

    def test_already_seen(self):
        as_ = AlreadySeen()
        self.assertTrue(as_.is_unique(1))
        self.assertFalse(as_.is_unique(1))

    def test_iterate_callable(self):
        a = [1, 2, 3]
        b = lambda i: a[i]
        self.assertEqual(list(iterate_callable(b)), [1, 2, 3])

    def test_f_range(self):
        self.assertRaises(TypeError, f_range)
        self.assertRaises(TypeError, lambda: f_range(1, 2, 3, 4))
        self.assertEqual(list(f_range(0.5, 1.5, 0.5)), [0.5, 1.0])
        self.assertEqual(list(f_range(0.5, -1.0, -0.5)), [0.5, 0.0, -0.5])

    def test_try_close(self):
        def iterator():
            yield 2

        a = iterator()
        try_close(a)
        try_close(iter([1, 2, 3]))

    def test_index_of_max(self):
        self.assertRaises(ValueError, lambda: index_of_max([]))
        self.assertEqual(index_of_max([1, 3, 2]), 1)

    def test_index_of(self):
        self.assertEqual(index_of(x == 2, [1, 2, 3]), 1)
        self.assertRaises(ValueError, lambda: index_of(x == 3, [1, 2, 4]))

    def test_filter_out_false(self):
        a = [0, 1, 2, 3, 4, False, None]
        self.assertEqual(filter_out_false(a), [1, 2, 3, 4])

    def test_filter_out_nones(self):
        a = [0, 1, 2, 3, 4, False, None]
        self.assertEqual(filter_out_nones(a), [0, 1, 2, 3, 4, False])

    def test_to_iterator(self):
        @to_iterator
        def is_even(x):
            return not (x % 2)

        self.assertEqual(list(is_even([1, 2, 3, 4])), [False, True, False, True])

    def test_infinite_iterator(self):
        if1 = infinite_iterator(1)
        for _ in range(100):
            self.assertEqual(next(if1), 1)
        if2 = infinite_iterator(return_factory=lambda: 1)
        for _ in range(100):
            self.assertEqual(next(if1), 1)

    def test_enumerate2(self):
        a = [1, 2, 3, 4]
        self.assertEqual(list(enumerate2(a, -1, -1)), [(-1, 1), (-2, 2), (-3, 3), (-4, 4)])

    def test_rolling_arith_avg(self):
        a = RollingArithmeticAverage(10)
        for i in range(10):
            a.insert(1)
        self.assertEqual(a.avg(), 1)
        a.insert(5)
        self.assertGreaterEqual(a.avg(), 1)
        self.assertLessEqual(len(a.queue), 10)
        self.assertEqual(a.tot_sum, 9+5)

    def test_make_list(self):
        a = [1, 2, 3]
        b = make_list(a, 3)
        self.assertEqual(len(b), 3)
        b[0][2] = 4
        self.assertNotEqual(b[1][2], 4)

    def test_make_list_deep_copy(self):
        class A:
            def __init__(self, c):
                self.a = c
        a = A(3)
        b = make_list(a, 3, deep_copy=True)
        self.assertEqual(len(b), 3)
        b[0].a = 4
        self.assertNotEqual(a.a, 4)

    def test_empty(self):
        def empty_iterator():
            if False:
                yield 2

        e = empty_iterator()
        self.assertTrue(is_empty(e))
        self.assertFalse(is_empty([1]))

    def test_smart_zip(self):
        a1 = [(1, 1), (1, 2), (1, 3)]
        a2 = [1, 2, 3]
        a = list(smart_zip(a1, a2))
        self.assertEqual(a, [(1, 1, 1), (1, 2, 2), (1, 3, 3)])

    def test_map_list(self):
        _list = map_list(x*2, range(5))
        self.assertEqual(_list, [0, 2, 4, 6, 8])

    def test_length(self):
        def iterator():
            i = 0
            for i in range(10):
                if i == 3:
                    return
                yield i
        self.assertEqual(length(iterator()), 3)

    def test_unique(self):
        a = [1, 2, 3, 1, 2, 3]
        self.assertEqual(list(unique(a)), [1, 2, 3])

    def test_n_th(self):
        self.assertEqual(n_th(itertools.count()), 0)
        self.assertEqual(n_th(itertools.count(), 3), 3)

    def test_multirun_empty(self):
        a = Multirun([])
        a += 3
        self.assertFalse(a.sequence)

    def test_multirun(self):
        class Counter:
            def __init__(self, value=0):
                self.value = value

            def add(self, value):
                self.value += value

            def __iadd__(self, other):
                self.add(other)

            def __eq__(self, other):
                return self.value == other.value

        a = [Counter(2), Counter(3)]

        b = Multirun(a)
        self.assertTrue(b)
        b.add(3)
        self.assertEqual(a, [Counter(5), Counter(6)])

        b += 3
        self.assertEqual(a, [Counter(8), Counter(9)])

    def test_even_and_odd(self):
        a = [0, 1, 2, 3, 4, 5, 6]
        self.assertEqual(list(even(a)), [0, 2, 4, 6])
        self.assertEqual(list(odd(a)), [1, 3, 5])

    def test_count(self):
        self.assertEqual(list(count([None, None, None], 5, -2)), [5, 3, 1])

    def test_count_without_start(self):
        self.assertEqual(list(count([None, None, None])), [0, 1, 2])

    def test_other_sequence_no_longer_than(self):
        s1 = [1, 2, 3]
        s2 = [3, 4, 5, 6]
        self.assertEqual(list(other_sequence_no_longer_than(s1, s2)), [3, 4, 5])

    def test_shift(self):
        self.assertEqual(list(shift([1, 2, 3], 1)), [2, 3, 1])
        self.assertEqual(list(shift([1, 2, 3], -1)), [3, 1, 2])

    def test_iter_dict_of_list(self):
        a = {1: [1, 2, 3]}
        self.assertEqual(list(iter_dict_of_list(a)), [(1, 1), (1, 2), (1, 3)])

    def test_group_quantity(self):
        self.assertEqual(list(group_quantity(3, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])),
                         [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]])
        self.assertEqual(list(group_quantity(3, 'ala ma kota')), ['ala', ' ma', ' ko', 'ta'])

    def test_group_quantity_range(self):
        def test_iter():
            yield from range(10)

        self.assertEqual(list(group_quantity(3, test_iter())),
                         [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]])
        self.assertEqual(list(group_quantity(3, range(10))),
                         [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]])

    def test_stop_after(self):
        a = [1, 2, 3, 4, 5, 6, 7]
        a = list(stop_after(a, 2))
        self.assertEqual([1, 2], a)

    def test_zip_shifted(self):
        a = list(zip_shifted(([1, 2, 3, 4], 1), [1, 2, 3, 4]))
        self.assertEqual(a, [(2, 1), (3, 2), (4, 3), (1, 4)])

    def test_zip_shifted_negative(self):
        a = list(zip_shifted(([1, 2, 3, 4], -1), [1, 2, 3, 4]))
        self.assertEqual(a, [(4, 1), (1, 2), (2, 3), (3, 4)])

    def test_skip_first(self):
        a = [1, 2, 3, 4, 5]
        b = list(skip_first(a, 1))
        self.assertEqual(b, [2, 3, 4, 5])

    def test_half_cartesian(self):
        a = set(half_cartesian([1, 2, 3]))
        b = {(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)}
        self.assertEqual(a, b)

    def test_half_cartesian_include_same_pairs_false(self):
        a = set(half_cartesian([1, 2, 3], include_same_pairs=False))
        b = {(1, 2), (1, 3), (2, 3)}
        self.assertEqual(a, b)

    def test_add_next(self):
        self.assertEqual(list(add_next([1, 2, 3, 4, 5])),
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)])
        self.assertEqual(list(add_next([1])), [(1, None)])
        self.assertEqual(list(add_next([])), [])
        self.assertEqual(list(add_next([1, 2, 3, 4, 5], skip_last=True)),
                         [(1, 2), (2, 3), (3, 4), (4, 5)])

    def test_add_next_wrap_over(self):
        self.assertEqual(list(add_next([1, 2, 3, 4, 5], True)),
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)])

    def test_is_last(self):
        for is_last_flag, elem in is_last([1, 2, 3, 4, 5]):
            self.assertTrue(not is_last_flag ^ (elem == 5))

    def test_take_n(self):
        subset = take_n(infinite_counter(), 10)
        for a, b in zip(range(10), subset):
            self.assertEqual(a, b)

    def test_infinite_counter(self):
        p = infinite_counter(1)
        for i in range(1, 10):
            a = next(p)
            self.assertEqual(a, i)

    def test_choose_one(self):
        self.assertEqual(choose_one(x == 2, [1, 2, 3, 4, 5]), 2)
        self.assertEqual(choose(x % 2 == 0, [1, 2, 3, 4, 5]), 2)
        self.assertRaises(ValueError, lambda: choose_one(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
        self.assertRaises(ValueError, lambda: choose_one(lambda x: x == 0, [1, 2, 3, 4, 5]))

    def test_is_instance(self):
        objects = [object(), object(), [], [], object()]
        self.assertEqual(len(list(filter(is_instance(list), objects))), 2)
