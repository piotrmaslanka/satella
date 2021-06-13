import unittest
from queue import Queue
from threading import Thread
from time import sleep

from satella.coding import Monitor


class MonitorTest(unittest.TestCase):
    def test_synchronize_on(self):
        class TestedMasterClass(Monitor):
            def __init__(self):
                self.value = 0
                super().__init__()

            def get_locking_class(self):
                class LockingClass:
                    @Monitor.synchronize_on(self)
                    def get_value(self2):
                        self.value += 1

                return LockingClass()

        msc = TestedMasterClass()
        lc = msc.get_locking_class()

        class TesterThread(Thread):
            def run(self):
                lc.get_value()

        with Monitor.acquire(msc):
            TesterThread().start()
            sleep(0.1)
            self.assertEqual(msc.value, 0)
            with Monitor.release(msc):
                sleep(0.1)
                self.assertEqual(msc.value, 1)

    def test_release_contextmanager(self):
        class TestedClass(Monitor):
            def __init__(self, cqueue):
                self.cqueue = cqueue
                Monitor.__init__(self)

            @Monitor.synchronized
            def execute(self):
                self.cqueue.put(1)
                sleep(1)
                self.cqueue.get()

        class TesterThread(Thread):
            def __init__(self, tc):
                self.tc = tc
                Thread.__init__(self)

            def run(self):
                self.tc.execute()

        cq = Queue()
        cq.put(1)
        tc = TestedClass(cq)
        tt = TesterThread(tc)

        with Monitor.acquire(tc):
            with Monitor.release(tc):
                tt.start()
                sleep(0.4)
                self.assertEqual(cq.qsize(), 2)

    def test_release_contextmanager_syntax(self):
        class TestedClass(Monitor):
            def __init__(self, cqueue):
                self.cqueue = cqueue
                Monitor.__init__(self)

            @Monitor.synchronized
            def execute(self):
                self.cqueue.put(1)
                sleep(1)
                self.cqueue.get()

        class TesterThread(Thread):
            def __init__(self, tc):
                self.tc = tc
                Thread.__init__(self)

            def run(self):
                self.tc.execute()

        cq = Queue()
        cq.put(1)
        tc = TestedClass(cq)
        tt = TesterThread(tc)

        with tc:
            with Monitor.release(tc):
                tt.start()
                sleep(0.4)
                self.assertEqual(cq.qsize(), 2)

    def test_acquire_contextmanager(self):
        class TestedClass(Monitor):
            def __init__(self, cqueue):
                self.cqueue = cqueue
                Monitor.__init__(self)

            @Monitor.synchronized
            def execute(self):
                self.cqueue.put(1)
                sleep(1)
                self.cqueue.get()

        class TesterThread(Thread):
            def __init__(self, tc):
                self.tc = tc
                Thread.__init__(self)

            def run(self):
                self.tc.execute()

        cq = Queue()
        cq.put(1)
        tc = TestedClass(cq)
        tt = TesterThread(tc)

        with Monitor.acquire(tc):
            tt.start()
            sleep(0.4)
            self.assertEqual(cq.qsize(), 1)

    def test_monitoring(self):
        class TestedClass(Monitor):
            def __init__(self, cqueue):
                self.cqueue = cqueue
                Monitor.__init__(self)

            @Monitor.synchronized
            def execute(self):
                self.cqueue.put(1)
                sleep(1)
                self.cqueue.get()

        class TesterThread(Thread):
            def __init__(self, tc):
                self.tc = tc
                Thread.__init__(self)

            def run(self):
                self.tc.execute()

        q = Queue()
        tc = TestedClass(q)
        a, b = TesterThread(tc), TesterThread(tc)
        a.start(), b.start()

        while a.is_alive() or b.is_alive():
            sleep(0.1)
            self.assertNotEqual(q.qsize(), 2)

    def test_monitoring_synchronize_on_attribute(self):
        class TestedClass:
            def __init__(self, cqueue):
                self.cqueue = cqueue
                self.monitor = Monitor()

            @Monitor.synchronize_on_attribute('monitor')
            def execute(self):
                self.cqueue.put(1)
                sleep(1)
                self.cqueue.get()

        class TesterThread(Thread):
            def __init__(self, tc):
                self.tc = tc
                Thread.__init__(self)

            def run(self):
                self.tc.execute()

        q = Queue()
        tc = TestedClass(q)
        a, b = TesterThread(tc), TesterThread(tc)
        a.start(), b.start()

        while a.is_alive() or b.is_alive():
            sleep(0.1)
            self.assertNotEqual(q.qsize(), 2)
