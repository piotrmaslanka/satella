import unittest
import abc
import logging
from satella.coding import metaclass_maker, wrap_with, dont_wrap, rethrow_as, wraps, wrap_property


logger = logging.getLogger(__name__)


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

        class BaseClass(abc.ABC):
            pass

        def property_wrapper(prop):

            class Property(property):
                __isabstractmethod__ = False

                @rethrow_as(ValueError, KeyError)
                def __get__(self, instance, owner):
                    v = prop.__get__(instance, owner)
                    logger.warning(f'Returning {v}')
                    return v

            return wraps(prop)(Property())

        class Doubles(BaseClass, metaclass=wrap_with(callables=double,
                                                     properties=property_wrapper,
                                                     selector_callables=selector)):
            def return_four(self, x):
                return 2

            @property
            def key_error(self):
                raise ValueError()

            @dont_wrap
            def return_five(self, x):
                return 5

            def return_six(self, x):
                return 6

        print(dir(Doubles))

        a = Doubles()
        self.assertEqual(a.return_four(2), 4)
        self.assertEqual(a.return_five(2), 5)
        self.assertEqual(a.return_six(2), 6)
        self.assertRaises(KeyError, lambda: a.key_error)

    def test_wrap_property(self):

        def wrap_getter(fun):
            def inner(slf):
                try:
                    return fun(slf) * 2
                except TypeError:
                    return fun(slf) * 2
            return inner

        def wrap_setter(fun):
            def inner(slf, value):
                return fun(slf, value*2)
            return inner

        def wrap_deleter(fun):
            return lambda slf: None

        wrap_prop = wrap_property(wrap_getter, wrap_setter, wrap_deleter)

        class MyClass:
            def __init__(self):
                self._x = 5

            @property
            def x(self):
                return self._x

            @x.setter
            def x(self, value):
                self._x = value

            @x.deleter
            def x(self):
                del self._x

            x = wrap_prop(x)

        mc = MyClass()
        self.assertEqual(mc.x, 10)
        mc.x = 20
        self.assertEqual(mc.x, 80)
        del mc.x
        self.assertEqual(mc.x, 80)

