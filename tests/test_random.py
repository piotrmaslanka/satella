import unittest
from satella.random import shuffle_together, random_binary


class TestRandom(unittest.TestCase):
    def test_random_binary(self):
        self.assertFalse(random_binary(0))
        self.assertEqual(len(random_binary(10)), 10)

    def test_random(self):
        a = [(1, 2, 3), ('a', 'b', 'c')]
        b = zip(*shuffle_together(*a))
        self.assertEqual(set(b), {(1, 'a'), (2, 'b'), (3, 'c')})

        self.assertEqual(shuffle_together(), [])


