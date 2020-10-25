import unittest

from satella.coding import precondition, short_none, has_keys, update_if_not_none, postcondition
from satella.coding.decorators import for_argument
from satella.exceptions import PreconditionError


class TestTypecheck(unittest.TestCase):

    def test_for_argument_extended(self):
        @for_argument(int)
        def accept_default(a=5):
            return a

        self.assertEqual(accept_default(6), 6)
        self.assertEqual(accept_default(), 5)

    def test_for_argument_str(self):
        @for_argument('x*2')
        def accept_two(x):
            self.assertEqual(x, 2)
        accept_two(1)

    def test_postcondition(self):
        @postcondition(lambda x: x)
        def return_nothing():
            pass

        return_nothing()

    def test_postcondition_2(self):
        @postcondition('x')
        def return_nothing():
            pass

        return_nothing()

    def test_postcondition_3(self):
        @postcondition(lambda x: False)
        def return_nothing():
            pass

        self.assertRaises(PreconditionError, return_nothing)

    def test_update_if_not_none(self):
        a = {}
        update_if_not_none(a, 'k', 2)
        self.assertEqual(a['k'], 2)

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
        @precondition(a=None)
        def do_any(a):
            return a

        self.assertEqual(do_any(a=5), 5)

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
