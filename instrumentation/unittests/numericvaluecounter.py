from satella.instrumentation.counters import NumericValueCounter
from satella.instrumentation import NoData

import unittest

class NumericValueCounterTest(unittest.TestCase):

    def test_name(self):
        ivc = NumericValueCounter('test_counter')
        self.assertEqual(ivc.name, 'test_counter')

    def test_history(self):
        ivc = NumericValueCounter('test_counter', history=2)
        ivc.update(10)
        ivc.update(11)
        hp, hn = ivc.get_history()
        self.assertEqual(hp[1], 10)
        self.assertEqual(hn[1], 11)

    def test_enabled(self):
        ivc = NumericValueCounter('test_counter')
        ivc.disable()
        ivc.update(10)
        self.assertRaises(NoData, ivc.get_current)

    def test_current_value(self):
        ivc = NumericValueCounter('test_counter')
        ivc.update(10)
        self.assertEqual(ivc.get_current(), 10)
        ivc.update(20)
        self.assertEqual(ivc.get_current(), 20)