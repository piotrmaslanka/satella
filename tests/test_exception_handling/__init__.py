import os
import threading
import unittest

from satella.coding import silence_excs


class ExceptionHandlingTestCase(unittest.TestCase):
    def setUp(self):
        try:
            os.environ
        except AttributeError:
            os.environ = {}

    def tearDown(self):
        with silence_excs(ValueError):
            self.exception_handler.uninstall()

    def make_exception(self, fun=lambda: {}['wtf']):

        class Hello(threading.Thread):
            def __init__(self):
                super(Hello, self).__init__()

            def run(self):
                return fun()

        p = Hello()
        p.start()
        p.join()
