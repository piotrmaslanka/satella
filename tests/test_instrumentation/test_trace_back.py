# coding=UTF-8

from __future__ import print_function, absolute_import, division

import pickle
import unittest

from satella.instrumentation import Traceback


class TestTraceback(unittest.TestCase):
    def test_no_exc(self):
        tb = Traceback()

    def test_tb(self):

        try:
            loc = 'hello world'
            raise ValueError('hello')
        except ValueError:
            tb = Traceback()

            p_fmt = tb.pretty_format()

        self.assertTrue(p_fmt)
        print(p_fmt)

    def test_compression_happens(self):

        try:
            loc = ' ' * (10 * 1024 * 1024)
            raise ValueError('hello')
        except ValueError:
            tb = Traceback()

        self.assertLess(len(pickle.dumps(tb, -1)), 9 * 1024 * 1024)
