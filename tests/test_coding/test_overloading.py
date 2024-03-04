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
        fun('test')
