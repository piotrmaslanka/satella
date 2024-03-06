import os
import unittest

from satella.os import whereis, safe_listdir


class TestWhereis(unittest.TestCase):
    def test_whereis_python(self):
        """
        Note that it will fail on Windows unless you have PYTHON.EXE in your path
        """
        self.assertEqual(list(safe_listdir('test22')), [])
        execs = list(whereis('python'))
        self.assertTrue(os.path.exists(execs[1]))
        self.assertGreaterEqual(len(execs), 1)


