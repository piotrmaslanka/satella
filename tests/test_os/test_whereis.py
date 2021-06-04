import unittest

from satella.os import whereis


class TestWhereis(unittest.TestCase):
    def test_whereis_python(self):
        """
        Note that it will fail on Windows unless you have PYTHON.EXE in your path
        """
        execs = list(whereis('python'))
        self.assertGreaterEqual(len(execs), 1)
