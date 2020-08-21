import unittest


from satella.coding.predicates import between, one_of, length_is, length_less_than, \
    length_multiple_of


class TestPredicates(unittest.TestCase):
    def test_length_is_attribute(self):
        class Attr:
            def __init__(self, b):
                self.a = b

        a = Attr('ala')
        self.assertTrue(length_is(3, 'a')(a))
        self.assertFalse(length_is(4, 'a')(a))

    def test_length_is(self):
        a = 'ala'
        self.assertTrue(length_is(3)(a))
        self.assertFalse(length_is(4)(a))

    def test_length_less_than(self):
        a = 'ala'
        self.assertTrue(length_less_than(4)(a))
        self.assertFalse(length_less_than(3)(a))

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
