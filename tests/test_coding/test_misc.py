from satella.coding import update_key_if_not_none, overload, class_or_instancemethod, \
    update_key_if_true
import unittest


class TestCase(unittest.TestCase):

    def test_update_key_if_true(self):
        a = {5: False}
        update_key_if_true(a, 5, True, False)
        self.assertFalse(a[5])
        update_key_if_true(a, 5, True, True)
        self.assertTrue(a[5])

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
