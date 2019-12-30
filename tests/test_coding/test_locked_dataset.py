import unittest

from satella.coding.concurrent import LockedDataset
from satella.exceptions import ResourceLocked, ResourceNotLocked


class TestLockedDataset(unittest.TestCase):
    def test_locked_dataset(self):
        class MyDataset(LockedDataset):

            def __init__(self):
                super(MyDataset, self).__init__()
                with self:
                    self.counter = 0

            @LockedDataset.locked(blocking=False)
            def increment(self):
                self.counter += 1

        a = MyDataset()
        with a:
            self.assertRaises(ResourceLocked, lambda: a(blocking=False).__enter__())
            self.assertRaises(ResourceLocked, lambda: a.increment())

        a.increment()
        with a:
            self.assertEquals(a.counter, 1)

        self.assertRaises(ResourceNotLocked, lambda: a.counter)
