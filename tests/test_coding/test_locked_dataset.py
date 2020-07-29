import unittest

from satella.coding.concurrent import LockedDataset
from satella.coding.concurrent.locked_dataset import _get_internal
from satella.coding.structures import Singleton
from satella.exceptions import WouldWaitMore, ResourceNotLocked


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
            self.assertRaises(WouldWaitMore,
                              lambda: a(blocking=False).__enter__())
            self.assertRaises(WouldWaitMore, lambda: a.increment())

        a.increment()
        with a:
            self.assertEqual(a.counter, 1)

        self.assertRaises(ResourceNotLocked, lambda: a.counter)
        _get_internal(a)

    def test_locked_dataset_singleton(self):
        @Singleton
        class MyDataset(LockedDataset):

            def __init__(self):
                super(MyDataset, self).__init__()
                with self:
                    self.counter = 0

            @LockedDataset.locked(blocking=False)
            def increment(self):
                self.counter += 1

        with MyDataset():
            self.assertRaises(WouldWaitMore,
                              lambda: MyDataset()(blocking=False).__enter__())
            self.assertRaises(WouldWaitMore, lambda: MyDataset().increment())

        MyDataset().increment()
        with MyDataset():
            self.assertEqual(MyDataset().counter, 1)

        self.assertRaises(ResourceNotLocked, lambda: MyDataset().counter)
