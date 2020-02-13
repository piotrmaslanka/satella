import unittest

from satella.coding import for_argument, precondition, short_none, has_keys
from satella.exceptions import PreconditionError


class TestTypecheck(unittest.TestCase):

    def test_has_keys(self):
        p = has_keys(['a', 'b'])
        self.assertRaises(PreconditionError, lambda: p({'a': 3}))
        p({'a': 3, 'b': 4})

    def test_short_none(self):
        a = short_none('x == 2')
        self.assertTrue(a(2))
        self.assertIsNone(a(None))
        self.assertFalse(a(3))

    def test_precondition_none(self):
        @precondition(None)
        def do_any(a):
            return a
        self.assertEqual(a(5), 5)

    def test_precondition_kwargs(self):
        @precondition(value='x == 2')
        def kwarg(**kwargs):
            return kwargs['value']

        self.assertRaises(PreconditionError, lambda: kwarg(value=3))
        kwarg(value=2)

    def test_precondition(self):
        @precondition('len(x) == 1', lambda x: x == 1, None)
        def return_double(x, y, z):
            pass

        self.assertRaises(PreconditionError, lambda: return_double([], 1, 5))
        self.assertRaises(PreconditionError, lambda: return_double([1], 2, 5))
        return_double([1], 1, 'dupa')

    def test_precondition_fail(self):
        @precondition('len(x) == 1', lambda x: x == 1, None, None, None)
        def return_double(x, y, z):
            pass

        self.assertRaises(AssertionError, lambda: return_double([1], 1, 5))

    def test_forarg_kwords(self):
        @for_argument(int, typed=bool)
        def check(v1, typed='True'):
            if typed:
                return v1

        self.assertEqual(check('5'), 5)

    def test_forarg_shorter(self):
        @for_argument(int)
        def check(v1, v2):
            if v2 != 'str':
                raise ValueError()
            return v1

        self.assertEqual(check('5', 'str'), 5)

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
