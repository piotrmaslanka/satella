import unittest
from satella.coding.transforms import stringify_dict


class MyTestCase(unittest.TestCase):
    def test_stringify_dict(self):
        dct = {1: 2, 3: 4, 5: 6}
        self.assertEqual(stringify_dict(dct), {'1': '2', '3': '4', '5': '6'})
