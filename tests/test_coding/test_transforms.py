import unittest
from satella.coding.transforms import stringify


class MyTestCase(unittest.TestCase):
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
