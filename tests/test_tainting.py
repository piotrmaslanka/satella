import unittest

from satella.debug import TaintedObject, TaintingEnvironment, taint

class TestTainting(unittest.TestCase):
    def test_declare(self):
        self.assertRaises(RuntimeError, lambda: taint(5))

        with TaintingEnvironment() as env:
            a = 5
            b = taint(a)
            c = taint(b)
            self.assertIs(b, c)
            self.assertEqual(id(env), id(TaintingEnvironment.get_session_in_progress()))
            def fun(a, b, c):
                return a+b+c
            d = fun(a, b, c)
            self.assertIsInstance(d, TaintedObject)
            self.assertEqual(d, 15)
            self.assertIn(str(d), '15')
            self.assertIn(15, list(env.get_tainted_variables()))

        with TaintingEnvironment() as env:
            self.assertEqual(id(env), id(TaintingEnvironment.get_session_in_progress()))
