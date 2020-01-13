import unittest

from satella.coding.structures import Singleton


class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        @Singleton
        class MyClass(object):
            def __init__(self):
                self.a = 5

        a = MyClass()
        b = MyClass()

        a.a = 6

        self.assertEqual(b.a, 6)
