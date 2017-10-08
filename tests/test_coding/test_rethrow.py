# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
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