from satella.instrumentation.counters import NumericValueCounter
from satella.instrumentation import CounterCollection
from satella.instrumentation.exceptions import NoData, ObjectExists, ObjectNotExists

import unittest

class CounterCollectionTest(unittest.TestCase):

    def test_add_remove_counter(self):
        """Tests adding and removing a counter from a collection"""
        insmgr = CounterCollection('test_namespace', description=u'test')
        ctr = NumericValueCounter('a_counter')
        atr = NumericValueCounter('a_counter')

        insmgr.add(ctr)
        insmgr.add(atr)
        self.assertRaises(ObjectExists, insmgr.add, ctr)
        self.assertEquals(insmgr.description, u'test')
        insmgr.remove(ctr)
        self.assertRaises(ObjectNotExists, insmgr.remove, ctr)

    def test_add_remove_collection(self):
        """Tests adding and removing a collection from a collection"""
        insmgr = CounterCollection('test_namespace')
        ctr = CounterCollection('nested_child')

        insmgr.add(ctr)
        self.assertRaises(ObjectExists, insmgr.add, ctr)
        insmgr.remove(ctr)
        self.assertRaises(ObjectNotExists, insmgr.remove, ctr)

    def test_mass_disable_enable(self):
        """Tests enabling and disabling children from a namespace"""
        insmgr = CounterCollection('test_namespace')
        ctr = NumericValueCounter('a_counter', units=u'dogs')
        atr = NumericValueCounter('b_counter', description=u'hello')

        self.assertEquals(ctr.units, u'dogs')
        self.assertEquals(atr.description, u'hello')

        insmgr.add(ctr)
        insmgr.add(atr)

        insmgr.disable()
        self.assertEquals(ctr.enabled, False)
        self.assertEquals(atr.enabled, False)        

        insmgr.enable()
        self.assertEquals(ctr.enabled, True)
        self.assertEquals(atr.enabled, True)                