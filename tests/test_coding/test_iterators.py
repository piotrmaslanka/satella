import sys
import unittest

from satella.coding import SelfClosingGenerator, hint_with_length, chain
from satella.coding.sequences import smart_enumerate, ConstruableIterator, walk, \
    IteratorListAdapter, is_empty, ListWrapperIterator


class TestIterators(unittest.TestCase):

    def test_list_wrapper_iterator(self):
        a = {'count': 0}

        def iterate():
            nonlocal a

            a['count'] += 1
            yield 1
            a['count'] += 1
            yield 2
            a['count'] += 1
            yield 3

        lwe = ListWrapperIterator(iterate())
        self.assertEqual(list(iter(lwe)), [1, 2, 3])
        self.assertEqual(a['count'], 3)
        self.assertEqual(list(iter(lwe)), [1, 2, 3])
        self.assertEqual(a['count'], 3)
        lwe2 = ListWrapperIterator(iterate())
        self.assertEqual(lwe2[1:2], [2])
        self.assertEqual(a['count'], 5)
        self.assertEqual(lwe2[2], 3)
        self.assertEqual(a['count'], 6)
        self.assertEqual(lwe2[0:0], [])
        self.assertRaises(IndexError, lambda: lwe2[4])

    def test_is_empty_not_exhaust(self):
        def generator():
            yield 1
            raise ValueError()

        self.assertFalse(is_empty(generator(), exhaust=False))
        self.assertTrue(is_empty([], exhaust=False))

    def test_generator_list_adapter(self):
        gla = IteratorListAdapter(range(10))
        self.assertEqual(next(gla), 0)
        self.assertEqual(gla[0], 1)
        self.assertEqual(len(gla), 9)
        self.assertEqual(list(gla), list(range(1, 10)))

    def test_walk(self):
        a = [[1, 2, 3], 4, 5, 6, [7, 8, 9]]
        b = walk(a, lambda x: x if isinstance(x, list) else None, leaves_only=True)
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

    def test_smart_enumerate(self):
        a = [(1, 2), (3, 4), (5, 6)]
        b = list(smart_enumerate(a))
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
