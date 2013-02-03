from satella.instrumentation.counters import NumericValueCounter
from satella.instrumentation.exceptions import NoData

import unittest

class NumericValueCounterTest(unittest.TestCase):

    def test_name(self):
        ivc = NumericValueCounter('test_counter')
        self.assertEqual(ivc.name, 'test_counter')

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