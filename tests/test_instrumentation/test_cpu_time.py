import threading
import time
import unittest

from satella.instrumentation.cpu_time import calculate_occupancy_factor, sleep_cpu_aware, \
    CPUTimeAwareIntervalTerminableThread, get_own_cpu_usage, CPUTimeManager

from satella.time import measure

TERMINATOR = True


class TestCPUTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        CPUTimeManager.set_refresh_each('5s')

    def test_cpu_time_aware_terminable_thread_terminates(self):
        class TestingThread(CPUTimeAwareIntervalTerminableThread):
            def __init__(self):
                super().__init__('5s', 3, 0.5, terminate_on=ValueError)
                self.a = 0

            def loop(self) -> None:
                raise ValueError()

        TestingThread().start().terminate().join()

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

    def test_get_own_cpu_usage(self):
        global TERMINATOR
        def run():
            global TERMINATOR
            while TERMINATOR:
                pass
        thr = threading.Thread(target=run)
        usage = get_own_cpu_usage()     # start the thread
        thr.start()
        time.sleep(10)
        while usage is None:
            time.sleep(5)
            usage = get_own_cpu_usage()

        try:
            with measure(timeout=30) as m:
                while not m.timeouted:
                    time.sleep(10)
                    usage = get_own_cpu_usage()
                    if usage.user > 0.6:
                        break
                else:
                    self.fail('Timeout when waiting for significant CPU usage')
        finally:
            TERMINATOR = False
            thr.join()

    def test_sleep_except(self):
        c = time.monotonic()
        sleep_cpu_aware(1)
        self.assertGreaterEqual(time.monotonic() - c, 1)

    def test_calculate_occupancy_factor(self):
        c = calculate_occupancy_factor()
        self.assertGreaterEqual(c, 0)
        c = calculate_occupancy_factor()
        self.assertGreaterEqual(c, 0)
        for i in range(4):  # make at most 4 attempts
            if c < 1:
                break
            c = calculate_occupancy_factor()
