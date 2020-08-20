import unittest

from satella.coding import ListDeleter, DictDeleter


class TestDeleters(unittest.TestCase):
    def test_dict_deleter(self):
        a = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
        with DictDeleter(a) as ld:
            for key, value in ld.items():
                if key % 2 == 0:
                    ld.delete()

        self.assertEqual(a, {1: 2, 3: 4, 5: 6})

    def test_list_deleter_reversed(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]
        with ListDeleter(a) as ld:
            for v in reversed(ld):
                if v % 2:
                    ld.delete()
        self.assertEqual(a, [2, 4, 6, 8])

    def test_list_deleter(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]

        with ListDeleter(a) as ld:
            for v in ld:
                if v % 2 == 0:
                    ld.delete()

        self.assertEqual(a, [1, 3, 5, 7])
