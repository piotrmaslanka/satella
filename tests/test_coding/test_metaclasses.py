import unittest

from satella.coding import metaclass_maker, wrap_all_methods_with, dont_wrap


class MetaA(type):
    pass


class MetaB(type):
    pass


class A(metaclass=MetaA):
    pass


class B(metaclass=MetaB):
    pass


class AB(A, B, metaclass=metaclass_maker):
    pass


class TestMetaclasses(unittest.TestCase):
    def test_metaclasses(self):
        a = AB()

    def test_wrap_all_methods_with(self):
        def double(fun):
            return lambda slf, x: fun(slf, x) * 2

        def selector(fun):
            return 'six' not in fun.__name__

        class Doubles(metaclass=wrap_all_methods_with(double, selector=selector)):
            def return_four(self, x):
                return 2

            @dont_wrap
            def return_five(self, x):
                return 5

            def return_six(self, x):
                return 6

        a = Doubles()
        self.assertEqual(a.return_four(2), 4)
        self.assertEqual(a.return_five(2), 5)
        self.assertEqual(a.return_six(2), 6)
