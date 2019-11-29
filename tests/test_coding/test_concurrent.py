# coding=UTF-8
from __future__ import print_function, absolute_import, division
import unittest

from satella.coding import CallableGroup


class TestCallableGroup(unittest.TestCase):
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

