import unittest
from unittest.mock import Mock

from satella.db import transaction


class RealConnection:
    def __init__(self):
        self.cursor_called = 0
        self.commit_called = 0
        self.rollback_called = 0
        self.close_called = 0

    def cursor(self):
        self.cursor_called += 1
        return Mock()

    def commit(self):
        self.commit_called += 1

    def rollback(self):
        self.rollback_called += 1

    def close(self):
        self.close_called += 1


class TestDB(unittest.TestCase):
    def test_db(self):
        conn = RealConnection()

        @transaction(conn)
        def test(cur):
            pass

        test()

        self.assertEqual(conn.cursor_called, 1)
        self.assertEqual(conn.commit_called, 1)

    def test_db_imba(self):
        conn = RealConnection()

        @transaction(conn)
        def test(cur):
            raise ValueError()

        test()

        self.assertEqual(conn.cursor_called, 1)
        self.assertEqual(conn.rollback_called, 1)

    def test_db2(self):
        conn = RealConnection()
        a = transaction(conn)
        with a as cur:
            self.assertEqual(conn.cursor_called, 1)
            cur.execute('TEST')
        self.assertEqual(conn.commit_called, 1)
        try:
            with a as cur:
                raise ValueError()
        except ValueError:
            self.assertEqual(conn.commit_called, 1)
            self.assertEqual(conn.rollback_called, 1)
