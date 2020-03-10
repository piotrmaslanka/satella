import platform
import time
import unittest
import copy

from satella.coding.concurrent import TerminableThread, CallableGroup, Condition, MonitorList


class TestConcurrent(unittest.TestCase):

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
