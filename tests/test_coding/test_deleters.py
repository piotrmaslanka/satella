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

        a = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
        with DictDeleter(a) as ld:
            for key in ld.keys():
                if key % 2 == 0:
                    ld.delete()

        self.assertEqual(a, {1: 2, 3: 4, 5: 6})

        a = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
        with DictDeleter(a) as ld:
            for value in ld.values():
                key = value - 1
                if key % 2 == 0:
                    ld.delete()

        self.assertEqual(a, {1: 2, 3: 4, 5: 6})

    def test_list_deleter_reversed(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]
        with reversed(ListDeleter(a)) as ld:
            for v in ld:
                self.assertEqual(v, ld())
                self.assertEqual(v, ld.value)
                if v % 2:
                    ld.delete()
        self.assertEqual(a, [2, 4, 6, 8])

    def test_list_deleter_reversed_prev_next(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]

        with reversed(ListDeleter(a)) as ld:
            # Advance to the end of the list
            self.assertRaises(StopIteration, ld.prev)
            while True:
                # Advance to the start of the list
                try:
                    ld.next()
                except StopIteration:
                    break

            # Advance to the beginning of the list
            while True:
                try:
                    v = ld.prev()
                except StopIteration:
                    break
                if v % 2 == 0:
                    ld.delete()

            self.assertRaises(StopIteration, lambda: ld.prev())
        self.assertEqual(a, [1, 3, 5, 7])

    def test_list_deleter(self):
        a = [1, 2, 3, 4, 5, 6, 7, 8]

        with ListDeleter(a) as ld:
            for v in ld:
                if v % 2 == 0:
                    ld.delete()

        self.assertEqual(a, [1, 3, 5, 7])

        a = [1, 2, 3, 4, 5, 6, 7, 8]

        with ListDeleter(a) as ld:
            while True:
                try:
                    v = ld.next()
                except StopIteration:
                    break
                if v % 2 == 0:
                    ld.delete()

        self.assertEqual(a, [1, 3, 5, 7])

        a = [1, 2, 3, 4, 5, 6, 7, 8]

        with ListDeleter(a) as ld:
            # Advance to the end of the list
            self.assertRaises(StopIteration, lambda: ld.prev())
            while True:
                try:
                    v = ld.next()
                    print('upwards', v)
                except StopIteration:
                    break

            while True:
                try:
                    v = ld.prev()
                    print('backwards', v)
                except StopIteration:
                    break
                if v % 2 == 0:
                    ld.delete()

        self.assertEqual(a, [1, 3, 5, 7])
