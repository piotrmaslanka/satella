import unittest

from satella.coding.transforms import stringify, split_shuffle_and_join, one_tuple, \
    merge_series, pad_to_multiple_of_length, clip


class TestTransforms(unittest.TestCase):

    def test_clip(self):
        self.assertEqual(clip(5, 10, 15), 10)
        self.assertEqual(clip(25, 10, 15), 15)
        self.assertEqual(clip(12, 10, 15), 12)

    def test_pad_to_multiple_length(self):
        a = [1, 2, 3]
        a = pad_to_multiple_of_length(a, 16, None)
        self.assertTrue(len(a) % 16 == 0)

    def test_series_merger(self):
        s1 = [(100, 1), (200, 2), (300, 3)]
        s2 = ((100, 2), (200, 3), (300, 4))

        sm = merge_series(s1, s2)
        self.assertEqual(next(sm), (100, 1, 2))
        self.assertEqual(next(sm), (200, 2, 3))
        self.assertEqual(next(sm), (300, 3, 4))
        self.assertRaises(StopIteration, lambda: next(sm))

    def test_series_merger2(self):
        s1 = [(100, 1), (200, 2), (300, 3)]
        s2 = ((101, 2), (201, 3), (301, 4))

        sm = merge_series(s1, s2)
        self.assertEqual(next(sm), (101, 1, 2))
        self.assertEqual(next(sm), (200, 2, 2))
        self.assertEqual(next(sm), (201, 2, 3))
        self.assertEqual(next(sm), (300, 3, 3))
        self.assertEqual(next(sm), (301, 3, 4))
        self.assertRaises(StopIteration, lambda: next(sm))

    def test_series_merger_3(self):
        s1 = [(100, 1), (200, 2)]
        s2 = []

        sm = merge_series(s1, s2)

        self.assertRaises(StopIteration, lambda: next(sm))

    def test_series_merger_4(self):
        s1 = [(100, 1), (200, 2), (300, 3)]
        s2 = [(100, 1)]

        sm = merge_series(s1, s2)
        self.assertEqual(next(sm), (100, 1, 1))
        self.assertEqual(next(sm), (200, 2, 1))
        self.assertEqual(next(sm), (300, 3, 1))

        self.assertRaises(StopIteration, lambda: next(sm))

    def test_series_merger_5(self):
        s1 = [(100, 1), (200, 2), (300, 3)]
        sm = merge_series(s1)

        self.assertEqual(next(sm), (100, 1))
        self.assertEqual(next(sm), (200, 2))
        self.assertEqual(next(sm), (300, 3))
        self.assertRaises(StopIteration, lambda: next(sm))

    def test_merge_series(self):
        s1 = [(10, 'A'), (20, 'B')]
        s2 = [(15, 'C'), (17, 'D'), (21, 'E')]
        s3 = list(merge_series(s1, s2))
        self.assertEqual(s3, [(15, 'A', 'C'), (17, 'A', 'D'), (20, 'B', 'D'), (21, 'B', 'E')])

    def test_one_tuple(self):
        self.assertEqual(list(one_tuple([1, 2, 3])), [(1, ), (2, ), (3, )])

    def test_split_shuffle_and_join(self):
        x = [1, 2, 3, 4]
        x = split_shuffle_and_join(x, lambda y: y % 2 == 0)
        self.assertTrue(x == [1, 3, 2, 4] or x == [1, 3, 4, 2])

        x = [1, 2, 3, 4]
        x = split_shuffle_and_join(x, lambda y: y % 2 == 0, False)
        self.assertTrue(x == [2, 4, 1, 3] or x == [4, 2, 1, 3])

    def test_stringify(self):
        dct = {1: 2, 3: 4, 5: 6}
        self.assertEqual(stringify(dct), {'1': '2', '3': '4', '5': '6'})

        lst = [1, 2, 3, 4, 5]
        self.assertEqual(stringify(lst), ['1', '2', '3', '4', '5'])

        lst2 = [[1, 2, 3], 3, 4, 5]
        self.assertEqual(stringify(lst2), ['[1, 2, 3]', '3', '4', '5'])
        self.assertEqual(stringify(lst2, recursively=True), [['1', '2', '3'], '3', '4', '5'])

        dct2 = {1: [1, 2, 3]}
        self.assertEqual(stringify(dct2, recursively=True), {'1': ['1', '2', '3']})

        self.assertIsNone(stringify(None))
        self.assertEqual(stringify(None, str_none=True), str(None))
