from satella.coding.concurrent import CallableGroup

from satella.cassandra import parallel_for, wrap_future
import unittest


class TestCassandra(unittest.TestCase):
    def test_wrap_future(self):
        class MockCassandraFuture:
            def __init__(self):
                self.value = None
                self.callbacks = CallableGroup()
                self.errbacks = CallableGroup()

            def add_callback(self, callback):
                self.callbacks.add(callback)

            def add_errback(self, errback):
                self.errbacks.add(errback)

            def set_result(self, x):
                self.value = x
                if isinstance(x, Exception):
                    self.errbacks(x)
                else:
                    self.callbacks(x)

        mcf = MockCassandraFuture()
        wrapped = wrap_future(mcf)
        self.assertEqual(id(wrapped), id(wrap_future(wrapped)))
        a = {}

        def on_done(fut):
            if fut.exception() is None:
                a['success'] = True
            else:
                a['failure'] = True

        wrapped.add_done_callback(on_done)

        mcf.set_result(None)
        self.assertTrue(a['success'])

        mcf = MockCassandraFuture()
        wrapped = wrap_future(mcf)
        wrapped.add_done_callback(on_done)
        mcf.set_result(Exception())
        self.assertTrue(a['failure'])

    def test_parallel_for(self):
        class Cursor:
            def __init__(self):
                self.execute_times_called = 0
                self.result_times_called = 0
                self.execute_without_args_called = 0

            def result(self):
                self.result_times_called += 1
                return []

            def execute_async(self, query, args=None):
                if args is None:
                    self.execute_without_args_called += 1
                self.execute_times_called += 1
                return self

        cur = Cursor()
        list(parallel_for(cur, 'SELECT * FROM table', [(1,), (2, ), (3, )]))

        self.assertEqual(cur.execute_times_called, 3)
        self.assertEqual(cur.result_times_called, 3)

        list(parallel_for(cur, ['SELECT * FROM table',
                                'SELECT * FROM table2',
                                'SELECT * FROM table3'], [(1,), (2, ), (3, )]))

        self.assertEqual(cur.execute_times_called, 6)
        self.assertEqual(cur.result_times_called, 6)

        list(parallel_for(cur, ['SELECT * FROM table',
                                'SELECT * FROM table2',
                                'SELECT * FROM table3'], [None, None, None]))

        self.assertEqual(cur.execute_without_args_called, 3)

