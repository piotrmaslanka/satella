import signal
import unittest
import time
import multiprocessing
import os
import sys

from satella.coding.concurrent import call_in_separate_thread
from satella.time import measure, time_as_int, time_ms, sleep, ExponentialBackoff, \
    parse_time_string
from concurrent.futures import Future


class TestTime(unittest.TestCase):

    def test_exponential_backoff_earlier_wakeup(self):
        eb = ExponentialBackoff(start=5, limit=30)

        @call_in_separate_thread()
        def do_test():
            with measure() as m:
                eb.wait_until_available(2.5)
                self.assertTrue(eb.available)
            self.assertLessEqual(m(), 1.5)

        eb.failed()
        do_test()
        time.sleep(1)
        eb.success()

    def test_exponential_backoff_waiting_for_service_healthy(self):
        eb = ExponentialBackoff(start=2, limit=30)

        eb.failed()
        self.assertFalse(eb.available)
        self.assertFalse(eb.ready_for_next_check)
        with measure() as m:
            eb.wait_until_available()
        self.assertTrue(eb.ready_for_next_check)
        self.assertGreaterEqual(m(), 2)
        eb.success()
        self.assertTrue(eb.ready_for_next_check)
        self.assertTrue(eb.available)
        eb.failed()
        self.assertFalse(eb.available)
        with measure() as m:
            eb.sleep()
        self.assertGreaterEqual(m(), 2)

    def test_parse_time_string(self):
        self.assertEqual(parse_time_string('30m'), 30 * 60)
        self.assertEqual(parse_time_string('30h'), 30*60*60)
        self.assertEqual(parse_time_string('30w'), 30 * 7 * 24 * 60 * 60)
        self.assertEqual(parse_time_string(2), 2)
        self.assertEqual(parse_time_string(2.0), 2.0)

    def test_exponential_backoff(self):
        with measure() as measurement:
            eb = ExponentialBackoff()
            eb.failed()
            eb.sleep()
            eb.failed()
            eb.sleep()
        self.assertGreaterEqual(measurement(), 2+4)

    def test_measure(self):
        with measure(timeout=0.5) as measurement:
            self.assertFalse(measurement.timeouted)
            time.sleep(1)
            self.assertTrue(measurement.timeouted)

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
