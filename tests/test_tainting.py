import unittest

from satella.debug import TaintedObject, TaintingEnvironment


class TestTainting(unittest.TestCase):
    def test_declare(self):
        self.assertRaises(RuntimeError, lambda: TaintedObject(5))

        with TaintingEnvironment() as env:
            a = 5
            b = TaintedObject(a)
            c = TaintedObject(b)
            self.assertIs(b, c)

            def taint_me(a, b, c):
                return a+b+c
            d = taint_me(a, b, c)
            self.assertIsInstance(d, TaintedObject)
            self.assertEqual(d, 15)
            self.assertIn(15, list(env.get_tainted_variables()))
