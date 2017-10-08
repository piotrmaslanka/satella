# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding import rethrow_as, silence_excs


class TestStuff(unittest.TestCase):

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


        
