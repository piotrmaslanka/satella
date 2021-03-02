import time
import unittest

from satella.instrumentation.cpu_time import calculate_occupancy_factor, sleep_cpu_aware, \
    CPUTimeAwareIntervalTerminableThread


class TestCPUTime(unittest.TestCase):
    def test_cpu_time_aware_terminable_thread(self):
        class TestingThread(CPUTimeAwareIntervalTerminableThread):
            def __init__(self):
                super().__init__('5s', 3, 0.5)
                self.a = 0

            def loop(self) -> None:
                self.a += 1

        tt = TestingThread()
        tt.start()
        time.sleep(0.2)
        self.assertEqual(tt.a, 1)
        time.sleep(5)
        self.assertEqual(tt.a, 2)
        tt.terminate().join()

    def test_sleep_except(self):
        c = time.monotonic()
        sleep_cpu_aware(1)
        self.assertGreaterEqual(time.monotonic() - c, 1)

    def test_calculate_occupancy_factor(self):
        c = calculate_occupancy_factor()
        self.assertGreaterEqual(c, 0)
        c = calculate_occupancy_factor()
        self.assertGreaterEqual(c, 0)
        self.assertLessEqual(c, 1)
