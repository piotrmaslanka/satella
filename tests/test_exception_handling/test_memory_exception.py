import unittest
import threading
import logging
import sys

from satella.exception_handling import MemoryErrorExceptionHandler

logger = logging.getLogger(__name__)


class TestMemoryHandler(unittest.TestCase):
    def setUp(self) -> None:
        # simulate giving a CallableGroup
        self.meh = MemoryErrorExceptionHandler(custom_hook=lambda type_, value, traceback: [True])
        self.meh.install()

    def test_memory_error_exception_handler(self):

        class MyThread(threading.Thread):
            def run(self):
                raise MemoryError()

        mt = MyThread()
        mt.start()
        mt.join()
        self.assertFalse(self.meh._free_on_memory_error)
