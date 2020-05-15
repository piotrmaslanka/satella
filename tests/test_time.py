import unittest
import time
from satella.time import measure
from concurrent.futures import Future


class TestTime(unittest.TestCase):

    def test_measure_future(self):
        future = Future()
        measurement = measure(future)
        future.set_running_or_notify_cancel()
        time.sleep(1)
        future.set_result(2)
        self.assertEqual(future.result(), 2)
        self.assertGreaterEqual(measurement(), 1)

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

    def test_measure_method_decorator(self):
        class Test:
            @measure()
            def try_measure(self, measurement):
                time.sleep(0.5)
                return measurement()

        self.assertGreaterEqual(Test().try_measure(), 0.5)

    def test_resuming(self):
        a = measure()
        time.sleep(0.5)
        self.assertGreaterEqual(a(), 0.5)
        a.stop()
        time.sleep(0.5)
        self.assertLess(a(), 0.7)
        a.start()
        time.sleep(0.5)
        self.assertLess(a(), 1.2)
        self.assertRaises(TypeError, lambda: a.reset())
        a.stop()
        self.assertRaises(TypeError, lambda: a.stop())
        a.reset()
        time.sleep(0.5)
        self.assertGreaterEqual(a(), 0.5)
        self.assertLess(a(), 0.7)
