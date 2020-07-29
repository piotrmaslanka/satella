import sys
import unittest

from satella.coding import SelfClosingGenerator, hint_with_length, chain
from satella.coding.sequences import enumerate, ConstruableIterator, walk


class TestIterators(unittest.TestCase):

    def test_walk(self):
        a = [[1, 2, 3], 4, 5, 6, [7, 8, 9]]
        b = walk(a, lambda x: x if isinstance(x, list) else None, leafs_only=True)
        self.assertEqual(list(b), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_construable_iterator(self):
        a = ConstruableIterator([1, 2, 3])
        c = []
        for b in a:
            if b == 2:
                a.add(5)
            c.append(b)
        self.assertEqual(c, [1, 2, 3, 5])

    def test_chain(self):
        a = chain(1, 2, [3, 4, 5], 6, (i for i in range(2)))
        a = list(a)
        self.assertEqual(a, [1, 2, 3, 4, 5, 6, 0, 1])

    def test_enumerate(self):
        a = [(1, 2), (3, 4), (5, 6)]
        b = list(enumerate(a))
        self.assertEqual([(0, 1, 2), (1, 3, 4), (2, 5, 6)], b)

    def test_hint_with_length(self):
        def generator():
            yield from range(1000)

        g = hint_with_length(generator, 1000)()
        self.assertEqual(g.__length_hint__(), 1000)

    @unittest.skipUnless(sys.implementation.name == 'cpython', 'Not CPython, this needs deterministic GC')
    def test_self_closing_generator_function(self):
        a = {'done': False}

        def generator():
            for i in range(5):
                yield i
            a['done'] = True

        for b in SelfClosingGenerator(generator)():
            if b == 2:
                break

        self.assertTrue(a['done'])

    def test_self_closing_generator_function(self):
        a = {'done': False}

        def generator():
            for i in range(5):
                yield i
            a['done'] = True

        with SelfClosingGenerator(generator)() as gen:
            for b in gen:
                if b == 2:
                    break

        self.assertTrue(a['done'])
