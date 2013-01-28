from threading import Thread
from satella.threads import Monitor
from time import sleep
from Queue import Queue

import unittest

class MonitorTest(unittest.TestCase):


    def test_acquire_contextmanager(self):
        class TestedClass(Monitor):
            def __init__(self, cqueue):
                self.cqueue = cqueue
                Monitor.__init__(self)

            @Monitor.protect
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

            @Monitor.protect
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