import copy
import platform
import random
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, Future as PythonFuture

from satella.coding.concurrent import TerminableThread, CallableGroup, Condition, MonitorList, \
    LockedStructure, AtomicNumber, Monitor, IDAllocator, call_in_separate_thread, Timer, \
    parallel_execute, run_as_future, sync_threadpool, IntervalTerminableThread, Future, \
    WrappingFuture, PeekableQueue, SequentialIssuer, CancellableCallback, ThreadCollection, \
    BogusTerminableThread, SingleStartThread, FutureCollection
from satella.coding.concurrent.futures import call_in_future, ExecutorWrapper
from satella.coding.sequences import unique
from satella.exceptions import WouldWaitMore, AlreadyAllocated, Empty


class TestConcurrent(unittest.TestCase):

    def test_future_collection_exception(self):
        fc = FutureCollection([PythonFuture(), PythonFuture()])
        fc.set_running_or_notify_cancel()
        fc[0].set_exception(IndexError())
        fc[1].set_exception(ValueError())
        self.assertIsInstance(fc.exception(), IndexError)

    def test_future_collection_callbacks_one(self):
        a = {'count': 0}

        def callback(fut):
            nonlocal a
            a['count'] += 1

        fc = FutureCollection([PythonFuture(), PythonFuture()])
        fc.add_done_callback(callback, True)
        fc.set_running_or_notify_cancel()
        fc.set_result(None)
        self.assertEqual(a['count'], 1)

    def test_future_collection_callbacks(self):
        a = {'count': 0}

        def callback(fut):
            nonlocal a
            a['count'] += 1

        fc = FutureCollection([PythonFuture(), PythonFuture()])
        fc.add_done_callback(callback)
        fc.set_running_or_notify_cancel()
        fc.set_result(None)
        self.assertEqual(a['count'], 2)

    def test_future_collection_cancel(self):
        fc = FutureCollection([PythonFuture(), PythonFuture()])
        self.assertTrue(fc.set_running_or_notify_cancel())

        ##
        fc = FutureCollection([PythonFuture(), PythonFuture()])
        fc.cancel()
        self.assertFalse(fc.set_running_or_notify_cancel())

        ##

        fc = FutureCollection([PythonFuture(), PythonFuture()])
        fc[0].cancel()
        self.assertTrue(fc.set_running_or_notify_cancel())

    def test_future_collection(self):
        fut1 = PythonFuture()
        fut2 = PythonFuture()
        fs = [PythonFuture(), PythonFuture()]
        fut3 = PythonFuture()

        fc = FutureCollection([fut1, fut2])
        fc.add(fut3)
        fc += fs

        self.assertIs(fc[1], fut2)

        self.assertTrue(fc.set_running_or_notify_cancel())

        @call_in_separate_thread()
        def set_future_collection():
            fc.set_result(None)

        set_future_collection()
        fc.result()

    def test_single_start_thread(self):
        dct = {'a': 0}

        class SST(SingleStartThread):
            def run(self):
                nonlocal dct
                dct['a'] += 1

        sst = SST()
        self.assertEqual(dct['a'], 0)
        sst.start()
        time.sleep(0.2)
        self.assertEqual(dct['a'], 1)
        sst.start()
        time.sleep(0.2)
        self.assertEqual(dct['a'], 1)

    def test_bogus(self):
        bt = BogusTerminableThread()
        self.assertFalse(bt.is_alive())
        self.assertRaises(RuntimeError, bt.join)
        bt.start()
        self.assertRaises(RuntimeError, bt.start)
        self.assertRaises(WouldWaitMore, lambda: bt.join(1))
        self.assertTrue(bt.is_alive())
        bt.terminate()
        self.assertRaises(RuntimeError, bt.start)
        bt.join(2)

    def test_thread_collection(self):
        dct = {}

        class Threading(threading.Thread):
            def __init__(self, a):
                super().__init__()
                self.a = a

            def run(self):
                nonlocal dct
                dct[self.a] = True
                if self.a == 6:
                    time.sleep(5)

        self.assertGreaterEqual(len(ThreadCollection.get_currently_running()), 1)
        tc = ThreadCollection.from_class(Threading, [2, 3, 4])
        tc.daemon = False
        self.assertFalse(tc.is_alive())
        self.assertEqual(len(tc), 3)
        self.assertFalse(tc.daemon)
        for t in tc:
            self.assertIsInstance(t, Threading)
        tc.append(Threading(5)).add(Threading(6))
        tc.start()
        self.assertRaises(WouldWaitMore, lambda: tc.join(2))
        tc.terminate().join()
        self.assertEqual(dct, {2: True, 3: True, 4: True, 5: True, 6: True})

    def test_cancellable_callback(self):
        a = {'test': True}

        def y():
            nonlocal a
            a['test'] = False

        cg = CallableGroup()
        cc = CancellableCallback(y)
        cg.add(cc)
        cc.cancel()
        cg()
        self.assertTrue(a['test'])

    def test_sequential_issuer(self):
        si = SequentialIssuer()
        a = si.issue()
        b = si.issue()
        self.assertGreater(b, a)
        c = si.no_less_than(100)
        self.assertGreaterEqual(c, 100)
        d = si.issue()
        self.assertGreater(d, c)

    def test_peekable_queue_put_many(self):
        pkb = PeekableQueue()

        pkb.put_many([1, 2])

        self.assertEqual(pkb.get(), 1)
        self.assertEqual(pkb.get(), 2)

    def test_peekable_queue(self):
        pkb = PeekableQueue()

        @call_in_separate_thread()
        def put_to_queue():
            time.sleep(0.5)
            pkb.put(1)
        pkb.put(1)
        self.assertEqual(pkb.qsize(), 1)
        self.assertEqual(pkb.peek(), 1)
        self.assertEqual(pkb.qsize(), 1)
        self.assertEqual(pkb.get(), 1)
        self.assertEqual(pkb.qsize(), 0)
        put_to_queue()
        self.assertRaises(Empty, lambda: pkb.get(0.2))
        self.assertEqual(pkb.get(0.7), 1)
        put_to_queue()
        self.assertEqual(pkb.get(), 1)
        self.assertEqual(pkb.qsize(), 0)

    def test_future_on(self):
        fut = Future()
        a = {'success': False, 'exception': False}

        def on_success(arg):
            nonlocal a
            a['success'] = True

        def on_failure(exc_val):
            nonlocal a
            a['exception'] = True

        fut.on_success(on_success).on_failure(on_failure)
        fut.set_running_or_notify_cancel()
        fut.set_exception(RuntimeError())
        self.assertEqual(a, {'success': False, 'exception': True})

        fut = Future()
        a = {'success': False, 'exception': False}
        fut.on_success(on_success).on_failure(on_failure)
        fut.set_running_or_notify_cancel()
        fut.set_result(5)
        self.assertEqual(a, {'success': True, 'exception': False})

    def test_wrapped_executor(self):
        tpe = ThreadPoolExecutor(max_workers=2)
        tpe_w = ExecutorWrapper(tpe)
        a = {'test': False}

        def call_me():
            nonlocal a
            a['test'] = True

        fut = tpe_w.submit(call_me)
        self.assertIsInstance(fut, Future)
        sync_threadpool(tpe_w)
        self.assertTrue(a['test'])

    def test_wrapped_executor_nested(self):
        tpe = ThreadPoolExecutor(max_workers=2)
        tpe_w = ExecutorWrapper(ExecutorWrapper(tpe))
        a = {'test': False}

        def call_me():
            nonlocal a
            a['test'] = True

        fut = tpe_w.submit(call_me)
        self.assertIsInstance(fut, Future)
        sync_threadpool(tpe_w)
        self.assertTrue(a['test'])

    def test_call_in_future(self):
        a = {'test': False}

        def call_me(arg):
            nonlocal a
            a['test'] = arg
        tpe = ThreadPoolExecutor(max_workers=2)

        callable_ = call_in_future(tpe, call_me, True)
        self.assertFalse(a['test'])
        fut = callable_()
        self.assertIsInstance(fut, PythonFuture)
        sync_threadpool(tpe)
        self.assertTrue(a['test'])

    def test_wrapping_future(self):
        fut = PythonFuture()
        wrap = WrappingFuture(fut)
        self.assertEqual(wrap._state, fut._state)
        fut.set_running_or_notify_cancel()
        self.assertEqual(wrap._state, fut._state)
        fut.set_result(3)
        self.assertEqual(wrap.result(), 3)

    def test_wrapping_future_callback(self):
        fut = PythonFuture()
        wrap = WrappingFuture(fut)

        def transform_future(future):
            future.set_result(future.result() + 2)

        wrap.add_pre_done_callback(transform_future)
        self.assertEqual(wrap._state, fut._state)
        fut.set_running_or_notify_cancel()
        self.assertEqual(wrap._state, fut._state)
        fut.set_result(3)
        self.assertEqual(wrap.result(), 5)

    def test_future_chain(self):
        fut = Future()

        def assert_five(arg):
            self.assertEqual(arg, 5)

        fut.chain(assert_five)
        fut.set_running_or_notify_cancel()
        fut.set_result(5)

    def test_future(self):
        fut = Future()
        fut.set_running_or_notify_cancel()

        def transform_future(future):
            future.set_result(future.result() + 2)

        fut.add_pre_done_callback(transform_future)
        fut.set_result(2)
        self.assertEqual(fut.result(), 4)

    def test_future_exception(self):
        fut = Future()
        fut.set_running_or_notify_cancel()

        def transform_future(future):
            future.set_exception(ValueError())

        fut.add_pre_done_callback(transform_future)
        fut.set_exception(KeyError())
        self.assertRaises(ValueError, fut.result)

    def test_sync_threadpool(self):
        tp = ThreadPoolExecutor(max_workers=4)
        a = {'cond': 4}
        def wait():
            nonlocal a
            time.sleep(random.randint(0, 10) / 10)
            a['cond'] -= 1
        for _ in range(4):
            tp.submit(wait)
        sync_threadpool(tp)
        self.assertEqual(a['cond'], 0)

    def test_sync_threadpool_wait_max_error(self):
        tp = ThreadPoolExecutor(max_workers=1)
        tp.submit(lambda: time.sleep(3))
        self.assertRaises(WouldWaitMore, lambda: sync_threadpool(tp, 2))

    def test_sync_threadpool_wait_max_correct(self):
        tp = ThreadPoolExecutor(max_workers=1)
        tp.submit(lambda: time.sleep(0.4))
        sync_threadpool(tp, 2)

    def test_run_as_future(self):
        a = {}

        @run_as_future
        def sleep_and_set(b):
            time.sleep(2)
            a['set'] = b

        fut = sleep_and_set(True)
        self.assertNotIn('set', a)
        fut.result()
        self.assertTrue(a['set'])

        @run_as_future
        def raises():
            raise ValueError()

        fut = raises()
        self.assertRaises(ValueError, fut.result)

    def test_parallel_execute(self):
        a = {'times_called': 0}

        def return_a_future(j):
            fut = Future()
            fut.set_running_or_notify_cancel()
            if j % 2 == 0:
                fut.set_exception(Exception())
            else:
                fut.set_result(a['times_called'])
            a['times_called'] += 1
            return fut

        i = 0
        for result in parallel_execute(return_a_future, [(0,), (1,), (2,), (3,), (4,)]):
            if i % 2 == 0:
                self.assertIsInstance(result, Exception)
            else:
                self.assertEqual(result, i)
            i += 1
        self.assertEqual(5, a['times_called'])

    def test_timer_separate(self):
        a = {'test': False}

        def set_a():
            a['test'] = True

        tmr = Timer(1, set_a, spawn_separate=True)
        tmr.start()
        time.sleep(2)
        self.assertTrue(a['test'])

    def test_timer(self):
        a = {'test': False}

        def set_a():
            a['test'] = True

        tmr = Timer('1s', set_a)
        tmr.start()
        time.sleep(2)
        self.assertTrue(a['test'])

    def test_call_in_separate_thread(self):
        a = {}

        @call_in_separate_thread()
        def call_me():
            a['test'] = 2
            return 5

        fut = call_me()
        self.assertEqual(fut.result(), 5)
        self.assertEqual(a['test'], 2)

    def test_id_allocator_top_limit(self):
        id_alloc = IDAllocator(top_limit=10)
        for i in range(10):
            id_alloc.allocate_int()
        self.assertRaises(Empty, id_alloc.allocate_int)
        self.assertRaises(ValueError, lambda: id_alloc.mark_as_allocated(12))

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
        self.assertEqual(a + 1, 4)
        self.assertEqual(a - 1, 2)
        self.assertEqual(a * 1, 3)
        self.assertEqual(a / 1, 3.0)
        self.assertEqual(a // 1, 3)
        self.assertEqual(1 + a, 4)
        self.assertEqual(-1 + a, 2)
        self.assertEqual(1 * a, 3)
        self.assertEqual(1 / (a + 1), 0.25)
        self.assertEqual(1 // a, 0)
        self.assertEqual(2 ** a, 8)
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
        self.assertEqual(a ** 2, 9)
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

    def test_terminate_on_exception_in_prepare(self):
        slf = self

        class MyThread(TerminableThread):
            def __init__(self):
                super().__init__(terminate_on=(ValueError, KeyError))
                self.a = 0

            def prepare(self) -> None:
                raise ValueError()

            def loop(self) -> None:
                slf.fail('Cannot invoke loop on a terminated thread!')

        mt = MyThread()
        mt.start().join()

    def test_terminate_on_exception(self):
        class MyThread(TerminableThread):
            def __init__(self):
                super().__init__(terminate_on=(ValueError, KeyError))
                self.a = 0

            def loop(self) -> None:
                self.a += 1
                if self.a == 4:
                    raise ValueError()

        mt = MyThread()
        mt.start().join()
        mt.terminate()

    @unittest.skipUnless(sys.implementation.name == 'cpython', 'Does not work on PyPy :(')
    def test_condition(self):
        dct = {'a': False}
        slf = self
        cond = Condition()
        interlock_cond = Condition()

        class MyThread(TerminableThread):
            def run(self) -> None:
                self.safe_sleep(-2)
                self.safe_sleep(0.5)
                interlock_cond.notify()
                slf.assertRaises(WouldWaitMore, lambda: cond.wait(timeout=0.5))
                cond.wait(timeout=0.5, dont_raise=True)
                cond.wait()
                dct['a'] = True

        MyThread().start()
        interlock_cond.wait()
        self.assertFalse(dct['a'])
        time.sleep(2)
        cond.notify()
        time.sleep(0.1)
        self.assertTrue(dct['a'])

    def test_terminablethread_condition(self):
        a = {'dct': False}
        condition = Condition()
        slf = self

        class MyThread(TerminableThread):
            def __init__(self):
                super().__init__()

            def run(self) -> None:
                nonlocal a, slf, condition
                self.safe_wait_condition(condition, 5)
                a['dct'] = True
                slf.assertRaises(WouldWaitMore, lambda: self.safe_wait_condition(condition, 3))

        t = MyThread().start()
        time.sleep(0.2)
        self.assertTrue(t.is_alive())
        self.assertFalse(a['dct'])
        condition.notify()
        time.sleep(0.1)
        self.assertTrue(a['dct'])

    def test_terminate_on(self):
        dct = {'a': False}

        class MyThread(TerminableThread):
            def __init__(self):
                super().__init__(terminate_on=ValueError)

            def loop(self) -> None:
                nonlocal dct
                if dct['a']:
                    raise ValueError()

        t = MyThread().start()
        self.assertTrue(t.is_alive())
        time.sleep(1)
        self.assertTrue(t.is_alive())
        dct['a'] = True
        time.sleep(1)
        self.assertTrue(t.terminating)
        self.assertFalse(t.is_alive())

    def test_cg_proforma(self):
        cg = CallableGroup()
        a = {}
        cg.add(lambda: a.__setitem__('test', 'value'))
        cg()
        self.assertEqual(a['test'], 'value')

    def test_terminable_thread(self):
        class MyTerminableThread(TerminableThread):
            def prepare(self):
                self.a = 5

            def loop(self):
                self.a += 1
                time.sleep(0.5)

        mtt = MyTerminableThread()
        mtt.start()
        mtt.terminate().join()

    def test_interval_terminable_thread(self):
        class MyTerminableThread(IntervalTerminableThread):
            def __init__(self):
                super().__init__(1)
                self.a = 0
                self.overrun = False

            def prepare(self) -> None:
                self.a = 1

            def on_overrun(self, time_taken: float) -> None:
                self.overrun = True

            def loop(self) -> None:
                if self.a == 3:
                    time.sleep(3)
                self.a += 1

        mtt = MyTerminableThread()
        mtt.start()
        time.sleep(0.3)
        self.assertIn(mtt.a, (1, 2))
        self.assertFalse(mtt.overrun)
        time.sleep(1.2)
        self.assertFalse(mtt.overrun)
        time.sleep(4)
        self.assertTrue(mtt.overrun)
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
