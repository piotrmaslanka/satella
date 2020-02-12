import unittest
import typing as tp
import time
from satella.time import measure


class TestTime(unittest.TestCase):
    def test_measure(self):
        with measure() as measurement:
            time.sleep(0.5)

        self.assertGreaterEqual(measurement(), 0.5)

    def test_measure_decorator(self):
        @measure()
        def measured(measurement):
            time.sleep(0.5)
            self.assertGreaterEqual(measurement(), 0.5)
        measured()

