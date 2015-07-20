from satella.instrumentation.counters import StringValueCounter
from satella.instrumentation import NoData

import unittest

class StringValueCounterTest(unittest.TestCase):

    def test_name(self):
        ivc = StringValueCounter('test_counter')
        self.assertEqual(ivc.name, 'test_counter')

    def test_history(self):
        ivc = StringValueCounter('test_counter', history=2)
        ivc.update('qw')
        ivc.update('wq')
        hp, hn = ivc.get_history()
        self.assertEqual(hp[1], 'qw')
        self.assertEqual(hn[1], 'wq')

    def test_enabled(self):
        ivc = StringValueCounter('test_counter')
        ivc.disable()
        ivc.update('aha')
        self.assertRaises(NoData, ivc.get_current)

    def test_current_value(self):
        ivc = StringValueCounter('test_counter')
        ivc.update('aha')
        self.assertEqual(ivc.get_current(), 'aha')
        ivc.update('abc')
        self.assertEqual(ivc.get_current(), 'abc')