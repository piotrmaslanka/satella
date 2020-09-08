from satella.coding import update_key_if_not_none, overload
import unittest


class TestCase(unittest.TestCase):

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
