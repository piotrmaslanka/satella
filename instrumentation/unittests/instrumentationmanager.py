from satella.instrumentation.counters import IntegerValueCounter
from satella.instrumentation.insmgr import InstrumentationManager
from satella.instrumentation.exceptions import NoData, CounterExists, CounterNotExists

import unittest

class InstrumentationManagerTest(unittest.TestCase):

    def test_add_remove_counter(self):
        insmgr = InstrumentationManager('test_namespace')
        ctr = IntegerValueCounter('a_counter')

        insmgr.add_counter(ctr)
        self.assertRaises(CounterExists, insmgr.add_counter, ctr)
        insmgr.remove_counter(ctr)
        self.assertRaises(CounterNotExists, insmgr.remove_counter, ctr)

    def test_snapshot(self):
        insmgr = InstrumentationManager('test_namespace')
        ctr = IntegerValueCounter('a_counter')
        ctr.update(10)

        xtr = IntegerValueCounter('c_counter')

        insmgr.add_counter(ctr)
        insmgr.add_counter(xtr)

        snapshot = insmgr.get_snapshot()

        self.assertEquals(snapshot['a_counter'], 10)
        self.assertRaises(CounterNotExists, lambda: snapshot['b_counter'])
        self.assertRaises(NoData, lambda: snapshot['c_counter'])
