import time
import unittest
from concurrent.futures import Future

from satella.coding.concurrent import call_in_separate_thread
from satella.coding.resources import CPManager


class TestResources(unittest.TestCase):
    def test_cp_manager(self):

        class Connection:
            total_connections = 0

            def __init__(self):
                self.i = 0
                Connection.total_connections += 1
                self.id = Connection.total_connections
                self.value_error_emitted = False
                self.closed = False

            def do(self):
                if self.closed:
                    raise RuntimeError('Connection closed')
                if self.value_error_emitted:
                    raise RuntimeError('do called despite raising ValueError earlier')
                self.i += 1
                if self.i == 3:
                    self.value_error_emitted = True
                    raise ValueError()
                elif self.i > 3:
                    raise RuntimeError('called too often')

            def close(self):
                self.closed = True

        class InheritCPManager(CPManager):
            def __init__(self, *args):
                super().__init__(*args)
                self.already_acquired = set()

            def create_connection(self) -> Connection:
                return Connection()

            def acquire_connection(self):
                v = super().acquire_connection()
                print(f'Acquiring connection {v.id}')
                if v.id in self.already_acquired:
                    raise RuntimeError('Reacquiring an acquired connection')
                self.already_acquired.add(v.id)
                return v

            def release_connection(self, connection) -> None:
                print(f'Releasing connection {connection.id}')
                self.already_acquired.remove(connection.id)
                super().release_connection(connection)

            def teardown_connection(self, connection) -> None:
                connection.close()

        cp = InheritCPManager(5, 3)

        conns = [cp.acquire_connection() for _ in range(5)]

        @call_in_separate_thread(daemon=True)
        def do_call():
            for _ in range(10):
                conn = cp.acquire_connection()
                time.sleep(1)
                try:
                    conn.do()
                except ValueError:
                    cp.fail_connection(conn)

                cp.release_connection(conn)

        ret = do_call()  # type: Future
        ret2 = do_call()
        cp.release_connection(conns.pop())
        cp.release_connection(conns.pop())
        ret.result(timeout=20)
        ret2.result(timeout=20)
        for i in range(20):
            conn = cp.acquire_connection()
            try:
                conn.do()
            except ValueError:
                cp.fail_connection(conn)
            cp.release_connection(conn)

        while conns:
            cp.release_connection(conns.pop())
        del cp
