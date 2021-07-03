import unittest

from satella.coding import assert_equal, Inequal


class TestDeepCompare(unittest.TestCase):
    def assertInequal(self, a, b):
        self.assertRaises(Inequal, lambda: assert_equal(a, b))

    def test_compare(self):
        assert_equal(2, 2)
        assert_equal(2.0, 2.0)
        assert_equal(None, None)
        assert_equal('test', 'test')
        assert_equal(b'test', b'test')
        self.assertInequal(3, 2)
        self.assertInequal([], [6])
        self.assertInequal({1: 2}, {3: 4})
        self.assertInequal({1: 2}, {1: 4})
        self.assertInequal({1: 2}, {3: 4, 5: 6})
        assert_equal([1], [1])
        assert_equal(set([1, 2]), set([2, 1]))

        class Object:
            def __init__(self, a):
                self.a = a

            def __eq__(self, other):
                return self.a == other.a

        assert_equal(Object(3), Object(3))
        self.assertInequal(Object(3), Object(4))
