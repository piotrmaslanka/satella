from satella.instrumentation.counters import PulseCounter
from satella.instrumentation.exceptions import NoData

from time import sleep

import unittest

class PulseCounterTest(unittest.TestCase):

    def test_name(self):
        ivc = PulseCounter('pulse_counter', resolution=1)
        self.assertEqual(ivc.name, 'pulse_counter')

    def test_enabled(self):
        ivc = PulseCounter('test_counter')
        ivc.disable()
        ivc.update()
        self.assertEquals(ivc.get_current(), 0)    

    def test_inline_update(self):
        ivc = PulseCounter('pulse_counter', resolution=1)
        ivc.update()
        ivc.update()
        self.assertEqual(ivc.get_current(), 2)

    def test_half_pulse_update(self):
        ivc = PulseCounter('pulse_counter', resolution=0.2)
        ivc.update()
        sleep(0.3)
        ivc.update()
        self.assertEqual(ivc.get_current(), 1)

    def test_bug_1(self):
        ivc = PulseCounter('c', resolution=60)
        ivc.update()
        ivc.update()
        self.assertEqual(ivc.get_current(), 2)
        sleep(3)        
        ivc.update()
        ivc.update()
        self.assertEqual(ivc.get_current(), 4)