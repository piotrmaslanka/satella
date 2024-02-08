import unittest

from satella.coding.var_managers import Context, get_current_context, THREADED_ROOT


class TestVarManagers(unittest.TestCase):
    def test_var_managers(self):
        par = Context()

        cls = Context(parent=par)
        cls.set('test', 2)
        self.assertEqual(cls.test, 2)

    def test_global(self):
        ctxt = THREADED_ROOT
        self.assertTrue(ctxt is get_current_context())

    def test_lookup(self):
        par1 = Context()
        par1.test = 5
        par2 = Context(parent=par1)
        par2.test = 5

        self.assertIn(par1, list(par2.lookup('test')))
        self.assertIn(par2, list(par2.lookup('test')))
