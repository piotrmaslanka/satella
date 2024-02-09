import unittest

from satella.coding.var_managers import Context, get_current_context, current
from satella.coding import var_managers


class TestVarManagers(unittest.TestCase):
    def test_var_mgr(self):
        mgr = get_current_context()
        with mgr.activate() as data:
            data.test = 5
        self.assertRaises(AttributeError, lambda: current.test)

    def test_var_managers(self):
        par = Context()

        cls = Context(parent=par)
        cls.test = 2
        self.assertEqual(cls.test, 2)

    def test_global(self):
        self.assertTrue(var_managers.THREADED_ROOT is get_current_context())

    def test_lookup(self):
        par1 = Context()
        par1.test = 5
        par2 = Context(parent=par1)
        par2.test = 5

        self.assertIn(par1, list(par2.lookup('test')))
        self.assertIn(par2, list(par2.lookup('test')))

    def test_get_current_context(self):
        cc = get_current_context()
        cc.test = 5
        assert cc.test == 5
        c2 = cc.new_context()
        c2.test2 = 4
        self.assertRaises(AttributeError, lambda: cc.test2)
