import unittest
from satella.random import shuffle_together


class TestRandom(unittest.TestCase):
    def test_random(self):
        a = [(1, 2, 3), ('a', 'b', 'c')]
        b = zip(shuffle_together(*a))
        self.assertEqual(set(b), {(1, 'a'), (2, 'b'), (3, 'c')})

