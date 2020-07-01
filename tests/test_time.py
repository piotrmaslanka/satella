import signal
import unittest
import time
import multiprocessing
import os
import sys
from satella.time import measure, time_as_int, time_ms, sleep
from concurrent.futures import Future


class TestTime(unittest.TestCase):

    @unittest.skipIf('win' in sys.platform, 'Needs POSIX to run')
    def test_sleep(self):
        sleep(-2)

        def runner():
            time.sleep(1)
            os.kill(os.getppid(), signal.SIGINT)

        multiprocessing.Process(target=runner).start()

        try:
            with measure() as measurement:
                sleep(3)
            self.assertGreaterEqual(measurement(), 3)
        finally:
            os.wait()

        multiprocessing.Process(target=runner).start()

        try:
            with measure() as measurement:
                sleep(3, True)
            self.assertLessEqual(measurement(), 3)
        finally:
            os.wait()

    def test_times(self):
        self.assertIsInstance(time_as_int(), int)
        self.assertIsInstance(time_ms(), int)

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

        for i in range(3):
            self.assertTrue(0.5 <= Test().try_measure() <= 0.7)

    def test_measure_method_decorator_stopped(self):
        class Test:
            @measure(create_stopped=True)
            def try_measure(self, measurement):
                time.sleep(0.3)
                measurement.start()
                time.sleep(0.5)
                return measurement()

        for i in range(3):
            self.assertTrue(0.5 <= Test().try_measure() <= 0.7)

    def test_resuming(self):
        a = measure()
        self.assertRaises(TypeError, lambda: a.start())
        time.sleep(0.5)
        self.assertGreaterEqual(a(), 0.5)
        a.stop()
        time.sleep(0.5)
        self.assertLess(a(), 0.7)
        a.start()
        time.sleep(0.5)
        self.assertLess(a(), 1.2)
        a.stop()
        self.assertRaises(TypeError, lambda: a.stop())
        a.reset_and_start()
        time.sleep(0.5)
        self.assertGreaterEqual(a(), 0.5)
        self.assertLess(a(), 0.7)
