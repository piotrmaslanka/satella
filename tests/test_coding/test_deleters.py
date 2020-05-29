import unittest

from satella.coding import ListDeleter


class TestDeleters(unittest.TestCase):
    def test_list_deleter(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]

        with ListDeleter(a) as ld:
            for v in ld:
                if v % 2 == 0:
                    ld.delete()

        self.assertEqual(a, [1, 3, 5, 7])
