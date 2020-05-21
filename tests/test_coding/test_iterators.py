import sys
import unittest

from satella.coding import SelfClosingGenerator, hint_with_length


class TestIterators(unittest.TestCase):
    def test_hint_with_length(self):
        def generator():
            for i in range(1000):
                yield i

        g = hint_with_length(generator, 1000)()
        self.assertEqual(g.__length_hint__(), 1000)

    @unittest.skipUnless(sys.implementation.name == 'cpython', 'Not CPython, this needs deterministic GC')
    def test_self_closing_generator_function(self):
        a = {'done': False}

        def generator():
            for i in range(5):
                yield i
            a['done'] = True

        for a in SelfClosingGenerator(generator)():
            if a == 2:
                break

        self.assertTrue(a['done'])
