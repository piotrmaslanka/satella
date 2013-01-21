from satella.instrumentation.counters.deltacounter import DeltaCounter
from satella.instrumentation.exceptions import NoData

import unittest

class DeltaCounterTest(unittest.TestCase):

    def test_delta(self):
        ivc = DeltaCounter('test_counter')
        self.assertEqual(ivc.get_current(), 0)
        ivc.update(5)
        self.assertEqual(ivc.get_current(), 5)
        ivc.update(-3)
        self.assertEqual(ivc.get_current(), 2)
