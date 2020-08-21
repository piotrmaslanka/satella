import unittest


from satella.coding.predicates import between, one_of


class TestPredicates(unittest.TestCase):
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
