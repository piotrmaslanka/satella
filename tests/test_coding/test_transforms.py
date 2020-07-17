import unittest

from satella.coding.transforms import stringify, split_shuffle_and_join


class MyTestCase(unittest.TestCase):
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
