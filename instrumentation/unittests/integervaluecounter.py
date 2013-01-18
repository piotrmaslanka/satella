from satella.instrumentation.counters import IntegerValueCounter

import unittest

class IntegerValueCounterTest(unittest.TestCase):

    def setUp(self):
        self.ivc = IntegerValueCounter('test_counter')

    def test_name(self):
        self.assertEqual(self.ivc.name, 'test_counter')

    def test_current_value(self):
        self.ivc.update(10)
        self.assertEqual(self.ivc.get_current(), 10)
        self.ivc.update(20)
        self.assertEqual(self.ivc.get_current(), 20)