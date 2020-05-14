import platform
import time
import unittest
import copy
import threading
import time

from satella.coding.concurrent import TerminableThread, CallableGroup, Condition, MonitorList, \
    LockedStructure, AtomicNumber


class TestConcurrent(unittest.TestCase):

    def test_atomic_number_wait(self):
        an = AtomicNumber()

        def process_atomic_number(a):
            time.sleep(0.3)
            a += 1

        self.assertEqual(an, 0)
        threading.Thread(target=process_atomic_number, args=(an, )).start()
        an.wait()
        self.assertEqual(an, 1)

    def test_atomic_number(self):
        a = AtomicNumber(4)
        a -= 1
        self.assertIsInstance(a, AtomicNumber)
        self.assertEqual(a, 3)

        self.assertIsInstance(a+2, int)

    def test_locked_structure(self):
        class MyLockedStructure:
            def __call__(self, *args, **kwargs):
                return 5

            def __init__(self, a, b, c):
                self.a = a
                self.b = b
                self.c = c

        mls = MyLockedStructure(1, 2, 3)
        ls = LockedStructure(mls)

        ls.b = 5
        with ls:
            self.assertEqual(mls.b, 5)
            self.assertEqual(mls.a, 1)
            self.assertEqual(mls(), 5)

    def test_copy_monitor_list(self):
        ml = MonitorList([1,2,3])
        ml2 = copy.copy(ml)
        self.assertEqual(ml2, ml)

    def test_condition(self):

        dct = {'a': False}
        cond = Condition()

        class MyThread(TerminableThread):
            def run(self) -> None:
                cond.wait()
                dct['a'] = True

        MyThread().start()
        self.assertFalse(dct['a'])
        cond.notify()
        time.sleep(0.1)
        self.assertTrue(dct['a'])

    def test_cg_proforma(self):
        cg = CallableGroup()
        a = {}
        cg.add(lambda: a.__setitem__('test', 'value'))
        cg()
        self.assertEqual(a['test'], 'value')

    def test_terminable_thread(self):
        class MyTerminableThread(TerminableThread):
            def loop(self):
                time.sleep(0.5)

        mtt = MyTerminableThread()
        mtt.start()
        mtt.terminate().join()

    @unittest.skipIf(platform.python_implementation() == 'PyPy', 'force=True doesn''t work on PyPy')
    def test_terminable_thread_force(self):
        class MyTerminableThread(TerminableThread):
            def run(self):
                a = 0
                while True:
                    time.sleep(0.5)
                    a += 1

        mtt = MyTerminableThread(daemon=True)
        mtt.start()
        mtt.terminate(force=True)
        mtt.join(3)
        self.assertFalse(mtt.is_alive())

    def test_callable_group_some_raise(self):
        cg = CallableGroup(gather=True)
        cg.add(lambda: dupa)
        cg.add(lambda: 5)
        self.assertRaises(NameError, lambda: cg())

        cg = CallableGroup(gather=True, swallow_exceptions=True)
        cg.add(lambda: dupa)
        cg.add(lambda: 5)
        self.assertEqual(cg()[1], 5)
        self.assertIsInstance(cg()[0], NameError)

    def test_callable_group(self):
        a = {
            'a': False,
            'b': False
        }

        opF = lambda what: lambda: a.__setitem__(what, True)

        cg = CallableGroup()

        cg.add(opF('a'))
        cg.add(opF('b'))

        cg()

        self.assertTrue(all(a.values()))
