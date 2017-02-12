# coding=UTF-8

from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.instrumentation import Traceback


class TestTraceback(unittest.TestCase):
    def test_tb(self):

        try:
            raise ValueError('hello')
        except:
            tb = Traceback()

            p_fmt = tb.pretty_format()

        self.assertTrue(p_fmt)