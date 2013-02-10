from satella.db.pool import DatabaseDefinition, ConnectionPool
from satella.threads import BaseThread
from time import sleep

import unittest

import psycopg2         # only if you want to use PostgreSQL for this test

class PoolTest(unittest.TestCase):

    # Sadly, here you are required to determine your very own database settings
    #   sample definition for PostgreSQL via psycopg2 follows
    dd = DatabaseDefinition(
            psycopg2.connect,
            psycopg2.OperationalError,
            (),
            {
                'database': 'postgres',
                'user': 'postgres',
                'password': 'mypassword',
                'host': 'example.com',
            })

    def test_databasedefinition_open_close(self):
        """Tests whether a connection can be made and closed
        via a DatabaseDefinition object"""

        self.dd.get_connection().close()

    def test_pool_simple_query(self):
        """Creates a pool with a single connection and does SELECT 2+2 with that"""
        cp = ConnectionPool(self.dd)
        with cp.cursor() as cur:
            cur.execute('SELECT 2+2')
            a, = cur.fetchone()

        self.assertEquals(a, 4)

        cp.close()

    def test_pool_simple_query_executemany(self):
        """Creates a pool with a single connection and does SELECT 2+2 with that with executemany"""
        cp = ConnectionPool(self.dd)
        with cp.cursor() as cur:
            cur.executemany('SELECT 2+2', ())

        cp.close()

    def test_transaction(self):
        """Creates a pool with a single connection and does a simple transaction on it"""
        cp = ConnectionPool(self.dd)
        with cp.transaction() as cur:
            cur.execute('SELECT 2+2')
            cur.execute('SELECT 2+2')
            cur.execute('SELECT 2+2')

        cp.close()

    def test_cursorwrapper_destructor(self):
        cp = ConnectionPool(self.dd)
        c1 = cp.cursor()
        del c1  # at this point c1 should die

        import gc
        gc.collect() # PyPy could keep c1 alive, we need
                     # to ensure it's dead.

        self.assertEquals(cp.connections.qsize(), 1)

    def test_threads(self):
        """Pool, two threads, basic queries"""
        class TT(BaseThread):
            def __init__(self, cp, tc):
                BaseThread.__init__(self)
                self.cp = cp  #: connection pool
                self.tc = tc  #: core test case

            def run(self):
                for x in xrange(0, 10):
                    with self.cp.cursor() as cur:
                        cur.execute('SELECT 2+2')
                        a, = cur.fetchone()

                    self.tc.assertEquals(a, 4)

        cp = ConnectionPool(self.dd, 2)
        a = TT(cp, self)
        b = TT(cp, self)
        a.start(), b.start()

        cp.close()


