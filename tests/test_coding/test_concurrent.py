import copy
import platform
import sys
import threading
import time
import unittest

from satella.coding.concurrent import TerminableThread, CallableGroup, Condition, MonitorList, \
    LockedStructure, AtomicNumber, Monitor, IDAllocator
from satella.coding.sequences import unique
from satella.exceptions import WouldWaitMore, AlreadyAllocated


class TestConcurrent(unittest.TestCase):

    def test_id_allocator(self):
        id_alloc = IDAllocator()
        x = set([id_alloc.allocate_int(), id_alloc.allocate_int(), id_alloc.allocate_int()])
        y = x.pop()
        self.assertRaises(AlreadyAllocated, lambda: id_alloc.mark_as_allocated(y))
        x.add(y)
        self.assertTrue(set(unique(x)), x)
        id_alloc.mark_as_free(y)
        id_alloc.mark_as_allocated(y)

        for i in range(100):
            x.add(id_alloc.allocate_int())

        self.assertEqual(x, set(unique(x)))

        id_alloc = IDAllocator(9000)
        self.assertTrue(9000 <= id_alloc.allocate_int() <= 9009)
        self.assertTrue(9000 <= id_alloc.allocate_int() <= 9009)

    def test_atomic_number_timeout(self):
        """Test comparison while the lock is held all the time"""
        a = AtomicNumber(2)

        def process_atomic_number():
            with Monitor.acquire(a):
                time.sleep(3)

        threading.Thread(target=process_atomic_number).start()

        self.assertRaises(WouldWaitMore, lambda: a.wait_until_equal(3, timeout=1))

    def test_atomic_number_wait_equal(self):
        an = AtomicNumber()

        def process_atomic_number(a):
            time.sleep(1)
            a += 1

        threading.Thread(target=process_atomic_number, args=(an,)).start()
        self.assertRaises(WouldWaitMore, lambda: an.wait_until_equal(2, timeout=0.5))
        an.wait_until_equal(1, timeout=1)
        an.wait_until_equal(1)

        self.assertEqual(str(an), '1')
        self.assertEqual(repr(an), 'AtomicNumber(1)')

    def test_atomic_number(self):
        a = AtomicNumber(4)
        a -= 1
        self.assertIsInstance(a, AtomicNumber)
        self.assertEqual(a, 3)

        self.assertEqual(a << 1, 0b110)
        self.assertEqual(a >> 1, 1)
        self.assertEqual(1 << a, 0b1000)
        self.assertEqual(0b111000 >> a, 0b111)
        self.assertEqual(a >> 1, 1)
        self.assertIsInstance(a + 2, int)
        self.assertEqual(a | 4, 7)
        self.assertEqual(a & 2, 2)
        self.assertEqual(a ^ 3, 0)
        self.assertEqual(4 | a, 7)
        self.assertEqual(2 & a, 2)
        self.assertEqual(3 ^ a, 0)
        self.assertTrue(a > 1)
        self.assertTrue(a < 4)
        self.assertTrue(a >= 1)
        self.assertTrue(a <= 4)
        self.assertEqual(a+1, 4)
        self.assertEqual(a-1, 2)
        self.assertEqual(a*1, 3)
        self.assertEqual(a/1, 3.0)
        self.assertEqual(a//1, 3)
        self.assertEqual(1+a, 4)
        self.assertEqual(-1+a, 2)
        self.assertEqual(1*a, 3)
        self.assertEqual(1/(a+1), 0.25)
        self.assertEqual(1//a, 0)
        self.assertEqual(2**a, 8)
        a |= 4
        self.assertEqual(a, 7)
        a &= 3
        self.assertEqual(a, 3)
        a ^= 0
        self.assertEqual(a, 3)
        a <<= 1
        self.assertEqual(a, 0b110)
        a >>= 1
        self.assertEqual(a, 3)
        a /= 1
        self.assertEqual(a, 3.0)
        a //= 1
        self.assertEqual(a, 3)
        self.assertEqual(a**2, 9)
        a **= 2
        self.assertEqual(a, 9)
        self.assertEqual(+a, 9)
        self.assertTrue(bool(a))
        self.assertEqual(int(a), 9)
        self.assertEqual(float(a), 9.0)
        self.assertEqual(-a, -9)
        self.assertEqual(abs(a), 9)

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
        ml = MonitorList([1, 2, 3])
        ml2 = copy.copy(ml)
        self.assertEqual(ml2, ml)

    @unittest.skipUnless(sys.implementation.name == 'cpython', 'Does not work on PyPy :(')
    def test_condition(self):
        dct = {'a': False}
        cond = Condition()
        interlock_cond = Condition()

        class MyThread(TerminableThread):
            def run(self) -> None:
                self.safe_sleep(0.5)
                interlock_cond.notify()
                cond.wait()
                dct['a'] = True

        MyThread().start()
        interlock_cond.wait()
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

    @unittest.skipIf(platform.python_implementation() != 'PyPy', 'this requires PyPy')
    def test_terminable_thread_force_notimplementederror(self):
        class MyTerminableThread(TerminableThread):
            def run(self):
                a = 0
                while not self.terminating:
                    time.sleep(0.5)
                    a += 1

        mtt = MyTerminableThread(daemon=True)
        mtt.start()
        self.assertRaises(NotImplementedError, lambda: mtt.terminate(force=True))
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

        def op_f(what):
            return lambda: a.__setitem__(what, True)

        cg = CallableGroup()

        cg.add(op_f('a'))
        cg.add(op_f('b'))

        cg()

        self.assertTrue(all(a.values()))
