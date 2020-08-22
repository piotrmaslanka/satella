import unittest


from satella.coding.predicates import between, one_of, length_is, shorter_than, \
    length_multiple_of, attribute, equals, item, longer_than, is_not_none, not_equal, \
    has_attr, p_all, p_any


class TestPredicates(unittest.TestCase):

    def test_p_all(self):
        p = [1, 2]
        self.assertTrue(p_all(item(equals(1), 0), item(equals(2), 1))(p))
        self.assertFalse(p_all(item(equals(1), 0), item(equals(3), 1))(p))

    def test_p_any(self):
        p = [1, 2]
        self.assertTrue(p_any(item(equals(1), 0), item(equals(3), 1))(p))
        self.assertFalse(p_any(item(equals(4), 0), item(equals(3), 1))(p))

    def test_has_attr(self):
        class A:
            def __init__(self):
                self.b = 2
        a = A()
        self.assertTrue(has_attr('b')(a))
        self.assertFalse(has_attr('c')(a))

    def test_not_equal(self):
        self.assertTrue(not_equal(5)(6))
        self.assertFalse(not_equal(5)(5))

    def test_is_not_none(self):
        self.assertTrue(is_not_none()(6))
        self.assertFalse(is_not_none()(None))

    def test_longer_than(self):
        a = 'ala'
        self.assertTrue(longer_than(2)(a))
        self.assertFalse(longer_than(3)(a))

    def test_length_is_attribute(self):
        class Attr:
            def __init__(self, b):
                self.a = b

        a = Attr('ala')
        self.assertTrue(attribute('a', length_is(3))(a))
        self.assertFalse(attribute('a', length_is(4))(a))

    def test_length_is_item(self):
        a = [1, 2, 5]

        self.assertTrue(item(1, equals(2))(a))
        self.assertFalse(item(0, equals(2))(a))

    def test_length_is(self):
        a = 'ala'
        self.assertTrue(length_is(3)(a))
        self.assertFalse(length_is(4)(a))

    def test_shorter_than(self):
        a = 'ala'
        self.assertTrue(shorter_than(4)(a))
        self.assertFalse(shorter_than(3)(a))

    def test_length_multiple_of(self):
        a = 'ala '
        self.assertTrue(length_multiple_of(4)(a))
        self.assertFalse(length_multiple_of(3)(a))

    def test_one_of(self):
        two_or_five = one_of(2, 5)
        self.assertTrue(two_or_five(2))
        self.assertTrue(two_or_five(5))
        self.assertFalse(two_or_five(1))

    def test_between(self):
        between2_and_5 = between(2, 5)
        self.assertTrue(between2_and_5(2))
        self.assertTrue(between2_and_5(5))
        self.assertTrue(between2_and_5(3))
        self.assertFalse(between2_and_5(1))
        self.assertFalse(between2_and_5(6))
        between2_and_5 = between(2, 5, False, False)
        self.assertFalse(between2_and_5(2))
        self.assertFalse(between2_and_5(5))
        self.assertTrue(between2_and_5(3))
        self.assertFalse(between2_and_5(1))
        self.assertFalse(between2_and_5(6))
