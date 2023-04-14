import unittest

from satella.coding import source_to_function
from satella.coding.predicates import x, build_structure


class TestPredicates(unittest.TestCase):

    def test_source_to_function(self):
        y = source_to_function(x)
        self.assertEqual(y(5), 5)

    def test_build_structure(self):
        a = {x: x*2}
        b = [x, x*2, x*3]
        c = (x, x*2, x*3)
        self.assertEqual(build_structure(a, 2), {2: 4})
        self.assertEqual(build_structure(b, 2), [2, 4, 6])
        self.assertEqual(build_structure(c, 2), (2, 4, 6))
        self.assertEqual(build_structure([(x, [x, x+1, x+2]),
                                          (x+1, [x, x+1, x+2])], 2, dict),
                         {2: [2, 3, 4],
                          3: [2, 3, 4]})
        self.assertEqual(build_structure(2, 2), 2)

    def test_is_instance(self):
        self.assertEqual(x.type()(2), int)
        self.assertTrue(x.is_instance(str, int)('str'))
        self.assertTrue(x.is_instance(str, int)(5))
        self.assertFalse(x.is_instance(str, int)(5.0))

    def test_is_valid_schema(self):
        a = {"test": 5, "test2": "string"}
        self.assertTrue(x.is_valid_schema({"test": "int", "test2": "str"})(a))
        self.assertFalse(x.is_valid_schema({"test3": "str", "test2": "str"})(a))

    def test_has_p(self):
        class Object:
            def __init__(self):
                self.a = [1, 2, 3, 4, 5, 6]
        a = Object()
        self.assertTrue(x.a.has_p(x % 2 == 0)(a))
        a.a = [3, 5, 7, 9]
        self.assertFalse(x.a.has_p(x % 2 == 0)(a))

    def test_int(self):
        p = x.int()
        self.assertEqual(p('2'), 2)

    def test_bool_str(self):
        p = x.int().str()
        self.assertEqual(p(True), '1')
        p = x.false()
        self.assertTrue(p(False))
        self.assertFalse(p(True))

    def test_upper(self):
        p = x.upper()
        self.assertEqual(p('ala ma kota'), 'ALA MA KOTA')

    def test_instanceof(self):
        p = x.instanceof(int)
        self.assertTrue(p(2))
        self.assertFalse(p('2'))

    def test_has_keys(self):
        a = {'hello': 'world', 'hello2': 'world'}
        p = x.has_keys('hello', 'hello2')
        self.assertTrue(p(a))
        del a['hello']
        self.assertFalse(p(a))

    def test_joined_predicates(self):
        p = (x > 2) & (x < 6)
        self.assertTrue(p(4))
        self.assertFalse(p(1))
        self.assertFalse(p(8))

        p = (x < 2) | (x > 6)
        self.assertTrue(p(1))
        self.assertTrue(p(8))
        self.assertFalse(p(4))

    def test_ops(self):
        p = (x + 2) == 2
        self.assertTrue(p(0))
        self.assertFalse(p(1))
        p = (x - 2) == 0
        self.assertTrue(p(2))
        self.assertFalse(p(1))
        p = (x * 2) == 2
        self.assertTrue(p(1))
        self.assertFalse(p(2))
        p = (x / 2) == 1
        self.assertTrue(p(2))
        self.assertFalse(p(1))
        p = (x + 2) % 3 == 0
        self.assertTrue(p(1))
        self.assertFalse(p(2))

    def test_one_of(self):
        p = x.one_of(2, 3)
        self.assertTrue(p(2))
        self.assertTrue(p(3))
        self.assertFalse(p(4))

    def test_contains(self):
        p = x.inside(2)
        self.assertTrue(p([1, 2]))
        self.assertFalse(p([1, 3]))

    def test_getattr(self):
        class A:
            def __init__(self, a=2):
                self.attr = a

        p = x.attr == 2
        self.assertTrue(p(A()))
        self.assertFalse(p(A(3)))

    def test_getitem(self):
        p = x[0] == 1
        self.assertTrue(p([1, 2]))
        self.assertFalse(p([2, 2]))

    def test_len(self):
        p = x.length() == 2
        self.assertTrue(p([1, 2]))
        self.assertFalse(p([]))

    def test_equals(self):
        p = x == 2
        self.assertTrue(p(2))
        self.assertFalse(p(3))
        p = x > 2
        self.assertTrue(p(3))
        self.assertFalse(p(2))
        p = x < 2
        self.assertTrue(p(1))
        self.assertFalse(p(2))
        p = x >= 2
        self.assertTrue(p(2))
        p = x <= 2
        self.assertTrue(p(1))
        self.assertTrue(p(2))
        self.assertFalse(p(3))
        p = x != 2
        self.assertTrue(p(1))
        self.assertFalse(p(2))
