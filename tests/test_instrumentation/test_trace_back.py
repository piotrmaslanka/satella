import pickle
import sys
import unittest

from satella.instrumentation import Traceback


class TestTraceback(unittest.TestCase):
    def test_no_exc(self):
        self.assertRaises(ValueError, Traceback)

    def test_tb(self):

        try:
            loc = u'hello world'
            raise ValueError(u'hello')
        except ValueError:
            tb = Traceback()

            p_fmt = tb.pretty_format()
        else:
            self.fail('exception not raised')

        self.assertTrue(p_fmt)

    def test_issue_21(self):
        try:
            loc = u'hello world'
            raise ValueError(u'hello')
        except ValueError:
            tb = Traceback()
            a = tb.pickle()
            self.assertIsInstance(pickle.loads(a), Traceback)

    def test_normal_stack_frames(self):
        tb = Traceback(list(sys._current_frames().values())[0])
        tb.pretty_format()

    def test_compression_happens(self):

        try:
            loc = ' ' * (10 * 1024 * 1024)
            raise ValueError('hello')
        except ValueError:
            tb = Traceback()

        self.assertLess(len(pickle.dumps(tb, -1)), 9 * 1024 * 1024)
