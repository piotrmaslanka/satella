import itertools
import unittest

from satella.coding.sequences import choose, choose_one, infinite_counter, take_n, is_instance, \
    is_last, add_next, half_cartesian, skip_first, zip_shifted, stop_after, group_quantity, \
    iter_dict_of_list, shift, other_sequence_no_longer_than, count, even, odd, Multirun, n_th, \
    unique, length


class TestSequences(unittest.TestCase):

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
        self.assertEqual(choose_one(lambda x: x == 2, [1, 2, 3, 4, 5]), 2)
        self.assertEqual(choose(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]), 2)
        self.assertRaises(ValueError, lambda: choose_one(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
        self.assertRaises(ValueError, lambda: choose_one(lambda x: x == 0, [1, 2, 3, 4, 5]))

    def test_is_instance(self):
        objects = [object(), object(), [], [], object()]
        self.assertEqual(len(list(filter(is_instance(list), objects))), 2)
