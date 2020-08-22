import unittest


from satella.coding.predicates import x


class TestPredicates(unittest.TestCase):

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
        p = 2 in x
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
