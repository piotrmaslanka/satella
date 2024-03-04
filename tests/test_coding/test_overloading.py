import unittest

from satella.coding import overload, TypeSignature


class TestOverloading(unittest.TestCase):
    def test_type_signature(self):
        def a(a: object):
            pass

        def b(a: int):
            pass

        self.assertLess(TypeSignature.from_fun(a), TypeSignature.from_fun(b))

    def test_something(self):
        @overload
        def fun(i: int):
            self.assertIsInstance(i, int)

        @fun.overload
        def fun(i: str):
            self.assertIsInstance(i, str)

        fun(2)
        self.assertRaises(TypeError, lambda: fun(2.5))
        fun('test')

    def test_something_2(self):
        class A:
            pass

        class B(A):
            pass

        @overload
        def fun(a: B):
            self.assertEquals(type(a), B)

        @fun.overload
        def fun(a: A):
            self.assertEquals(type(a), A)

        fun(A())
        fun(B())
