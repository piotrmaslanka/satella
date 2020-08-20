from satella.coding import update_key_if_not_none
import unittest


class TestCase(unittest.TestCase):
    def test_update_key_if_not_none(self):
        a = {}
        update_key_if_not_none(a, 'test', None)
        update_key_if_not_none(a, 'test2', 2)
        self.assertEqual(a, {'test2': 2})
