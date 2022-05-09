import time
import unittest
from concurrent.futures import Future

from satella.coding.concurrent import call_in_separate_thread

from satella.coding.resources import CPManager


class TestResources(unittest.TestCase):
    def test_something(self):
        class InheritCPManager(CPManager):
            def __init__(self, *args):
                super().__init__(*args)
                self.resources = 0

            def create_connection(self):
                time.sleep(3)
                self.resources += 1
                return lambda: self.resources + 1

            def teardown_connection(self, connection) -> None:
                ...

        cp = InheritCPManager(5, 2)

        conns = [cp.acquire_connection() for _ in range(5)]

        @call_in_separate_thread()
        def do_call():
            conn = cp.acquire_connection()
            cp.release_connection(conn)

        ret = do_call()     # type: Future
        cp.release_connection(conns.pop())
        ret.result(timeout=5)

        while conns:
            cp.release_connection(conns.pop())
        del cp
