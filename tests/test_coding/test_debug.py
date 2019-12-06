# coding=UTF-8
from __future__ import print_function, absolute_import, division

import unittest

from satella.coding import for_argument, precondition
from satella.exceptions import PreconditionError


class TestTypecheck(unittest.TestCase):
    def test_precondition(self):
        @precondition('len(x) == 1', lambda x: x == 1, None)
        def return_double(x, y, z):
            pass

        self.assertRaises(PreconditionError, lambda: return_double([], 1, 5))
        self.assertRaises(PreconditionError, lambda: return_double([1], 2, 5))
        return_double([1], 1, 'dupa')

    def test_forarg_kwords(self):
        @for_argument(int, typed=bool)
        def check(v1, typed='True'):
            if typed:
                return v1

        self.assertEquals(check('5'), 5)

    def test_forarg_shorter(self):
        @for_argument(int)
        def check(v1, v2):
            if v2 != 'str':
                raise ValueError()
            return v1

        self.assertEquals(check('5', 'str'), 5)

    def test_forarg_returns(self):
        @for_argument(returns=bool)
        def check(v1, v2):
            return v1 and v2

        self.assertTrue(check('dupa', 'zbita'))

    def test_forarg(self):
        @for_argument(int)
        def testa(a):
            return a

        self.assertEqual(testa('5'), 5)
        self.assertEqual(testa(5), 5)
        self.assertIsInstance(testa('5'), int)
