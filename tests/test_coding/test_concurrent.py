# coding=UTF-8
from __future__ import print_function, absolute_import, division
import unittest

from satella.coding import CallableGroup


class TestCallableGroup(unittest.TestCase):
    def test_callable_group_some_raise(self):
        cg = CallableGroup(gather=True)
        cg.add(lambda: dupa)
        cg.add(lambda: 5)
        self.assertRaises(NameError, lambda: cg())

        cg = CallableGroup(gather=True, swallow_exceptions=True)
        cg.add(lambda: dupa)
        cg.add(lambda: 5)
        self.assertEquals(cg()[1], 5)
        self.assertIsInstance(cg()[0], NameError)

    def test_callable_group(self):

        a = {
            'a': False,
            'b': False
        }

        opF = lambda what: lambda: a.__setitem__(what, True)

        cg = CallableGroup()

        cg.add(opF('a'))
        cg.add(opF('b'))

        cg()

        self.assertTrue(all(a.values()))

