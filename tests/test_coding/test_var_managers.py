import unittest

from satella.coding.var_managers import BaseContext


class TestVarManagers(unittest.TestCase):
    def test_var_managers(self):
        par = BaseContext()

        cls = BaseContext(parent=par)
        cls.set('test', 2)
        self.assertEqual(cls.test, 2)

