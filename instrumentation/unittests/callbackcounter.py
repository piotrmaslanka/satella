from satella.instrumentation.counters import CallbackCounter
from satella.instrumentation.exceptions import InstrumentationException, NoData

import unittest

class CallbackCounterTest(unittest.TestCase):

    def test_updates_not_allowed(self):
        ivc = CallbackCounter('test_counter', lambda: 0)
        self.assertRaises(InstrumentationException, ivc.update)

    def test_disabling(self):
        ivc = CallbackCounter('test_counter', lambda: 0)
        ivc.disable()
        self.assertRaises(NoData, ivc.get_current)
        ivc.enable()
        self.assertEqual(ivc.get_current(), 0)

    def test_listsize(self):
        a_list = [1,2,3,4]
        ivc = CallbackCounter('test_counter', lambda: len(a_list))
                # in this case the callback can also be a_list.__len__

        self.assertEqual(ivc.get_current(), 4)
        a_list.extend([5,6,7])
        self.assertEqual(ivc.get_current(), 7)
        a_list.remove(1)
        self.assertEqual(ivc.get_current(), 6)
