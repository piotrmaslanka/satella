import unittest

from satella.coding import precondition, short_none, has_keys, update_if_not_none, postcondition, \
    get_arguments, expect_exception
from satella.coding.decorators import for_argument
from satella.exceptions import PreconditionError


class TestTypecheck(unittest.TestCase):

    def test_except_exception(self):
        def expect_exception_1():
            with expect_exception(KeyError, ValueError, 'Hello world!'):
                pass

        self.assertRaises(ValueError, expect_exception_1)

        a = {}
        with expect_exception(KeyError, ValueError, 'Hello world!'):
            a['test']

        def expect_exception_2():
            with expect_exception(KeyError, ValueError, 'Hello world!'):
                raise TypeError()

        self.assertRaises(TypeError, expect_exception_2)

    def test_for_argument_bug(self):
        class Device:
            @for_argument(None, str)
            def __init__(self, device_id: str, init_true: bool = False):
                self.device_id = device_id
                self.init_true = init_true

            def __eq__(self, other):
                return self.device_id == other.device_id

        d = Device(1234)
        self.assertEqual(d.device_id, '1234')
        self.assertFalse(d.init_true)

    def test_get_arguments_bug(self):
        class Class:

            @classmethod
            def execute(cls, password: str, service: str,
                        absolute_expiration=None,
                        metadata=None):
                pass

            def method_call(self, password: str, service: str,
                        absolute_expiration=None,
                        metadata=None):
                pass
        kls = Class()

        args = get_arguments(Class.execute, '1234',
                             'service', metadata={'ok': 'meta'})
        self.assertEqual(args, {
            'password': '1234',
            'service': 'service',
            'metadata': {'ok': 'meta'},
            'absolute_expiration': None
        })

        args = get_arguments(kls.method_call, '1234', 'service', metadata={'ok': 'meta'})
        self.assertEqual(args, {
            'password': '1234',
            'service': 'service',
            'metadata': {'ok': 'meta'},
            'absolute_expiration': None
        })

        self.assertRaises(TypeError, lambda: get_arguments(kls.method_call, '1234'))
        self.assertRaises(TypeError, lambda: get_arguments(Class.execute, '1234'))

    def test_for_argument_extended(self):
        @for_argument(int)
        def accept_default(a='5'):
            return a

        self.assertEqual(accept_default('6'), 6)
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
