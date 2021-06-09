import logging
import enum
import gc
import unittest

from satella.coding import update_key_if_not_none, overload, class_or_instancemethod, \
    update_key_if_true, get_arguments, call_with_arguments, chain_callables, Closeable, \
    contains, enum_value, for_argument
from satella.coding.structures import HashableMixin, ComparableEnum
from satella.coding.transforms import jsonify, intify

logger = logging.getLogger(__name__)

class TestCase(unittest.TestCase):

    def test_closeable_semi_initialized_classes(self):
        slf = self

        class Test(Closeable):
            def __init__(self):
                raise ValueError()
                self.a = 5
                super().__init__()

            def close(self):
                if super().close():
                    slf.fail('Tried to close an uninitialized class!')

        self.assertRaises(ValueError, Test)

    def test_cant_compare_me(self):
        class Uncomparable:
            def __eq__(self, other):
                raise TypeError()

            def __str__(self):
                return 'test'

        @for_argument(y=str)
        def test(y = Uncomparable()):
            return y

        b = test()
        self.assertEqual(b, 'test')

    def test_contains(self):
        class CEnum(ComparableEnum):
            A = 1
            B = 2

        a = [CEnum.A, CEnum.B]
        self.assertTrue(contains(2, a))
        self.assertFalse(contains(3, a))

        self.assertEqual(enum_value(CEnum.A), 1)
        self.assertEqual(enum_value(1), 1)

    def test_closeable(self):
        a = {'test': False}

        class MyClose(Closeable):
            def close(self):
                if super().close():
                    a['test'] = True

        b = MyClose()
        self.assertFalse(b.closed)
        del b
        gc.collect()
        self.assertTrue(a['test'])

    def test_chain_callables(self):
        def a():
            return 5

        def mul2(b):
            return b*2

        self.assertEqual(chain_callables(a, mul2)(), 10)

        def two():
            return 2

        self.assertEqual(chain_callables(a, two)(), 2)

    def test_hashable_mixin(self):
        class MixedIn(HashableMixin):
            pass

        a = MixedIn()
        b = MixedIn()

        self.assertNotEqual(hash(a), hash(b))
        self.assertNotEqual(a, b)

    def test_intify(self):
        self.assertEqual(intify(None), 0)
        self.assertEqual(intify('2'), 2)
        self.assertRaises(ValueError, lambda: intify(object()))
        self.assertEqual(intify([1, 2, 3]), 3)

    def test_execute_with_locals(self):
        def fun(a, b, *args, c=None, **kwargs):
            if len(kwargs):
                d = kwargs[next(iter(kwargs))]
            else:
                d = 0
            return a + b + args[0] + c + d

        self.assertEqual(call_with_arguments(fun, {
            'a': 5,
            'b': 5,
            'args': (5,),
            'c': 5
        }), 20)
        self.assertEqual(call_with_arguments(fun, {
            'a': 5,
            'b': 5,
            'args': (5,),
            'kwargs': {
                'd': 10,
            },
            'c': 5
        }), 30)
        self.assertRaises(TypeError, lambda: call_with_arguments(fun, {}))
        self.assertRaises(ValueError, lambda: call_with_arguments(fun, {
            'a': 5,
            'b': 5,
            'args': (5,),
            'd': 10,
            'c': 5
        }))

    def test_get_arguments(self):
        def fun(a, b, *args, c=None, **kwargs):
            ...

        self.assertRaises(TypeError, lambda: get_arguments(fun))
        self.assertEqual(get_arguments(fun, 3, 4, 5, 6, c=4, d=5),
                         {
                             'a': 3,
                             'b': 4,
                             'args': (5, 6),
                             'c': 4,
                             'kwargs': {
                                 'd': 5
                             }
                         })

        def fun(a=5, c=7, *args, d=8, **kwargs):
            ...

        self.assertEqual(get_arguments(fun), {
            'a': 5,
            'c': 7,
            'args': (),
            'd': 8,
            'kwargs': {}
        })

        def fun(a=6):
            ...

        self.assertEqual(get_arguments(fun, 7),
                         {'a': 7})

    def test_jsonify(self):
        def iterate():
            yield 5

        class StrFails:
            def __str__(self):
                raise TypeError()

        class Enu(enum.IntEnum):
            A = 0

        self.assertEqual(jsonify(Enu.A), 0)
        self.assertEqual(jsonify(iterate()), [5])
        self.assertEqual(jsonify([iterate(), iterate()]), [[5], [5]])
        self.assertEqual(jsonify({'5': iterate()}), {'5': [5, ]})
        self.assertTrue(isinstance(jsonify(StrFails()), str))

    def test_update_key_if_true(self):
        a = {5: False}
        update_key_if_true(a, 5, True, False)
        self.assertFalse(a[5])
        update_key_if_true(a, 5, True, True)
        self.assertTrue(a[5])
        update_key_if_true(a, 6, True)
        self.assertTrue(a[6])

    def test_class_or_instancemethod(self):

        a = {}

        class MyClass:
            @class_or_instancemethod
            def method(self_or_cls):
                if isinstance(self_or_cls, MyClass):
                    a['method'] = True
                else:
                    a['classmethod'] = True

        b = MyClass()
        b.method()
        self.assertEqual(a, {'method': True})
        MyClass.method()
        self.assertEqual(a, {'method': True, 'classmethod': True})

    def test_overload(self):
        a = {}

        @overload
        def what_type(x: str):
            a['type'] = 'str'

        @what_type.overload
        def what_type(x: int):
            a['type'] = 'int'

        what_type('test')
        self.assertEqual(a['type'], 'str')
        what_type(2)
        self.assertEqual(a['type'], 'int')
        self.assertRaises(TypeError, lambda: what_type(2.0))

    def test_update_key_if_not_none(self):
        a = {}
        update_key_if_not_none(a, 'test', None)
        update_key_if_not_none(a, 'test2', 2)
        self.assertEqual(a, {'test2': 2})
        update_key_if_not_none(a, {'test3': 3, 'test4': None})
        self.assertEqual(a, {'test2': 2, 'test3': 3})
