from satella.coding import update_key_if_not_none, overload, class_or_instancemethod, \
    update_key_if_true, get_arguments, execute_with_locals
import unittest

from satella.coding.transforms import jsonify


class TestCase(unittest.TestCase):

    def test_execute_with_locals(self):
        def g(a):
            return a+5
        self.assertEqual(execute_with_locals(g, {'a': 5}), 10)

    def test_get_arguments(self):
        def fun(a, b, *args, c=None, **kwargs):
            ...

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

    def test_jsonify(self):
        def iterate():
            yield 5

        class StrFails:
            def __str__(self):
                raise TypeError()

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
