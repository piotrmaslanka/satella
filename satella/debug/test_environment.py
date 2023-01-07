import unittest

from satella.coding.environment import Context


class TestEnvs(unittest.TestCase):

    def test_envs(self):
        ctxt = Context.get()
        ctxt.value = 5
        self.assertEqual(ctxt.value, 5)
        with Context() as new_ctxt:
            self.assertEqual(new_ctxt.value, 5)

    def test_push(self):
        ctxt = Context.get()
        ctxt.value = 5
        self.assertEqual(ctxt.value, 5)
        with Context() as new_ctxt:
            self.assertEqual(new_ctxt.value, 5)
            with Context() as new_ctxt2:
                new_ctxt2.push_up('value', 6)
            self.assertEqual(new_ctxt.value, 6)

        self.assertEqual(ctxt.value, 5)

    def test_delete_envs(self):
        ctxt = Context.get()
        ctxt.value = 5
        self.assertEqual(ctxt.value, 5)
        with Context() as new_ctxt:
            del new_ctxt.value
            self.assertRaises(AttributeError, lambda: new_ctxt.value)
        self.assertEqual(ctxt.value, 5)

    def test_nesting(self):
        with Context() as ctxt:
            ctxt.value = 55
            with Context() as new_ctxt:
                new_ctxt.value = 66
                assert new_ctxt.value == 66
            assert ctxt.value == 55

