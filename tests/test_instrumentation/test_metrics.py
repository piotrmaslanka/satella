# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.instrumentation import instrument


class TestInstrumentsAndMetrics(unittest.TestCase):
    def test_detail(self):
        mk = instrument.getInstrument('core')
        mk.set_detail(instrument.DEBUG)

