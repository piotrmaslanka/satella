import unittest

from satella.coding.optionals import call_if_nnone, iterate_if_nnone, Optional, extract_optional


class TestOptionals(unittest.TestCase):

    def test_extract_optional(self):
        b = Optional(None)
        self.assertIs(extract_optional(b.test.value), None)
        self.assertEqual(extract_optional(5), 5)

    def test_optional(self):
        b = Optional(None)
        self.assertFalse(b.consumer.cancel().result())

    def test_iterate(self):
        b = list(iterate_if_nnone([1, 2, 3]))
        c = list(iterate_if_nnone(None))
        self.assertFalse(c)
        self.assertTrue(b)

    def test_optional_lambda(self):
        Optional(None())
        Optional(lambda: 5)()

    def test_object(self):
        class Obj:
            def __init__(self):
                self.a = 5

        obj = Obj()
        opt = Optional(obj)
        Optional(None).a
        self.assertEqual(opt.a, 5)
        opt.a = 6
        self.assertEqual(obj.a, 6)
        self.assertEqual(opt.a, 6)
        del opt.a
        self.assertRaises(AttributeError, lambda: obj.a)
        self.assertRaises(AttributeError, lambda: opt.a)

    def test_list(self):
        a = [1, 2, 3]
        opt = Optional(a)
        self.assertEqual(opt[0], 1)
        del opt[0]
        self.assertEqual(len(opt), 2)
        opt[0] = 4
        self.assertEqual(opt[0], 4)

    def test_optional_eq(self):
        class Opt:
            a = 5
            b = [2]

        a = Opt()
        self.assertEqual(Optional(a).a, 5)
        self.assertIn(2, Optional(a).b)
        self.assertNotEqual(Optional(None).a, 5)
        self.assertNotIn(2, Optional(None).b)
        self.assertEqual(Optional(5), Optional(5))

    def test_optional(self):
        self.assertIsNone(call_if_nnone(None))
        b = call_if_nnone(lambda y: y, 5)
        self.assertIsNotNone(b)
        self.assertEqual(5, b)
