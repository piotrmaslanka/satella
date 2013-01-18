from satella.instrumentation.counters import PulseCounter

from time import sleep

import unittest

class PulseCounterTest(unittest.TestCase):

    def test_name(self):
        ivc = PulseCounter('pulse_counter', resolution=1)
        self.assertEqual(ivc.name, 'pulse_counter')

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