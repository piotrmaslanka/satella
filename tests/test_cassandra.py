from satella.cassandra import parallel_for
import unittest


class TestCassandra(unittest.TestCase):
    def test_parallel_for(self):
        class Cursor:
            def __init__(self):
                self.execute_times_called = 0
                self.result_times_called = 0

            def result(self):
                self.result_times_called += 1
                return []

            def execute_async(self, query, args):
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
