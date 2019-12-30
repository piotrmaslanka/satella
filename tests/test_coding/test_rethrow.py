# coding=UTF-8
from __future__ import print_function, absolute_import, division

import unittest

from satella.coding import rethrow_as, silence_excs


class TestStuff(unittest.TestCase):

    @silence_excs(ValueError)
    def test_silencer_2(self):
        raise ValueError()

    def test_silencer(self):
        with silence_excs(TypeError):
            raise TypeError()

    def test_rethrow(self):
        try:
            with rethrow_as((ValueError, NameError)):
                raise ValueError()
        except NameError:
            return

        self.fail()

    def test_rethrow_3(self):
        try:
            with rethrow_as(ValueError, NameError):
                raise ValueError()
        except NameError:
            return

        self.fail()

    def test_rethrow_2(self):

        @rethrow_as((ValueError, NameError))
        def lol():
            raise ValueError()

        self.assertRaises(NameError, lol)

    def test_issue_10(self):

        class WTFException1(Exception): pass

        class WTFException2(Exception): pass

        @rethrow_as((NameError, WTFException1),
                    (TypeError, WTFException2))
        def provide(exc):
            raise exc()

        self.assertRaises(WTFException1, lambda: provide(NameError))
        self.assertRaises(WTFException2, lambda: provide(TypeError))

    def test_issue_14a(self):

        @rethrow_as(*(((NameError, ValueError), TypeError),))
        def ro(p):
            raise p()

        self.assertRaises(TypeError, lambda: ro(NameError))
        self.assertRaises(TypeError, lambda: ro(ValueError))
        self.assertRaises(RuntimeError, lambda: ro(RuntimeError))

    def test_issue_14b(self):

        @rethrow_as((NameError, ValueError), TypeError)
        def ro(p):
            raise p()

        self.assertRaises(TypeError, lambda: ro(NameError))
        self.assertRaises(TypeError, lambda: ro(ValueError))
        self.assertRaises(RuntimeError, lambda: ro(RuntimeError))
