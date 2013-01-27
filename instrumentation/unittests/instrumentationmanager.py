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

    def test_severity(self):
        insmgr = InstrumentationManager('test_namespace')
        ctr = IntegerValueCounter('a_counter', severity=10)
        xtr = IntegerValueCounter('c_counter', severity=5)

        insmgr.add_counter(ctr)
        insmgr.add_counter(xtr)

        insmgr.set_severity(7)
        self.assertEquals(ctr.enabled, True)
        self.assertEquals(xtr.enabled, False)

        insmgr.set_severity(12)
        self.assertEquals(ctr.enabled, False)
        self.assertEquals(xtr.enabled, False)

        insmgr.set_severity(7)
        self.assertEquals(ctr.enabled, True)
        self.assertEquals(xtr.enabled, False)

        insmgr.set_severity(0)
        self.assertEquals(ctr.enabled, True)
        self.assertEquals(xtr.enabled, True)