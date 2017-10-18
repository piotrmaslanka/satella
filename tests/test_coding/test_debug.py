# coding=UTF-8
from __future__ import print_function, absolute_import, division

import unittest

import six

from satella.coding import typed, CallSignature, Number, coerce, Optional, \
    List, Dict, Tuple, Set, Callable, checked_coerce, for_argument, \
    precondition, PreconditionError


class TestTypecheck(unittest.TestCase):
    
    def test_precondition(self):

        @precondition('len(x) == 1', lambda x: x == 1, None)
        def return_double(x, y, z):
            pass

        self.assertRaises(PreconditionError, lambda: return_double([], 1, 5))
        self.assertRaises(PreconditionError, lambda: return_double([1], 2, 5))
        return_double([1], 1, 'dupa')
    
    def test_cls(self):
        # if we don't care about apps
        class Lol(object):
            @typed(returns=int)
            def zomg(self, a):
                return a

            @typed('self', List(int), Dict(str, int), Tuple(int), Set(int),
                   Callable(int, None))
            def lel(self, lst, dct, tpl, st, cbl):
                pass

        Lol().zomg(2)
        self.assertRaises(TypeError, lambda: Lol().zomg('a'))
        Lol().lel([], {}, (), set([1]), lambda a: None)

    def test_che_co2(self):

        @checked_coerce((int, None))
        def p(a):
            return a

        p(5)
        p(None)
        self.assertRaises(TypeError, lambda: p(5.0))

    def test_forarg(self):
        @for_argument(int)
        def testa(a):
            return a

        self.assertEqual(testa('5'), 5)
        self.assertEqual(testa(5), 5)
        self.assertIsInstance(testa('5'), int)

    def test_checked_coerce(self):

        @checked_coerce([(str, int), int], returns=(int, float))
        def testa(a):
            return a

        self.assertRaises(TypeError, lambda: testa(5.0))
        self.assertEqual(testa('5'), 5.0)
        self.assertEqual(testa(5), 5.0)
        self.assertIsInstance(testa('5'), float)

    def test_cls_test(self):
        class Lol(object):
            # this should fail, since the first argument the decorator gets is "self", because decorators always get FUNCTION objects!
            @typed(int, returns=int)
            def zomg(self, a):
                return a

        self.assertRaises(TypeError, lambda: Lol().zomg(2))

    def test_ta(self):
        @typed(int, int, returns=int)
        def sum(a, b):
            return a + b

        @typed(int, int, returns=str)
        def sum2(a, b):
            return a + b

        sum(1, 2)
        self.assertRaises(TypeError, lambda: sum2(2, 3))

    def test_tma(self):
        def test(a, b, c, **d):
            pass

        cs = CallSignature(test)

        self.assertTrue(cs.is_match_amount(1, 2, 3, wtf=4))
        self.assertFalse(cs.is_match_amount(1, 2, wtf=4))
        self.assertTrue(cs.is_match_amount(1, 2, 3))
        self.assertFalse(cs.is_match_amount(1, 2, 3, 4))

    def test_t1(self):
        @typed(int, float, six.text_type)
        def testf(a_int, a_float, a_string):
            pass

        self.assertRaises(TypeError, lambda: testf('lol', 15, b'test'))
        self.assertRaises(TypeError, lambda: testf(12, 2.0, b'hey'))
        testf(12, 2.0, u'hey')

        @typed((None, int, float))
        def testa(param):
            pass

        self.assertRaises(TypeError, lambda: testa('hey'))
        testa(2)
        testa(2)
        testa(2.0)

        @typed(None, int)
        def testb(a, num):
            pass

        testb(None, 100000000000000000000000000000000)
        testb(u'hello', 1)
        testb(object, 2)

        @typed((None,))
        def testc(p):
            pass

        self.assertRaises(TypeError, lambda: testc(2))
        testc(None)

    def test_t2(self):
        @typed(Optional(int))
        def testa(a=5):
            pass
        
        self.assertRaises(TypeError, lambda: testa(2.0))
        testa(a=2.0)
        self.assertRaises(TypeError, lambda: testa('yuyu'))
        testa(a=None)
        testa(a=6)

    def test_shorter_coerces(self):

        @coerce(int, None, str)
        def test(a, b, c, d, e):
            return a, b, c, d, e

        a, b, c, d, e = test('1', 2, 3, 4, 5)

        self.assertEqual(a, 1)
        self.assertEqual(b, 2)
        self.assertEqual(c, '3')
        self.assertEqual(d, 4)
        self.assertEqual(e, 5)

    def test_coerce(self):
        class Wtf(object):
            @coerce('self', float, float)
            def add(self, a, b):
                return a + b

        self.assertEqual(Wtf().add('1', '2.5'), 3.5)

    def test_coerce_result(self):

        @coerce(returns=str)
        def add(a, b):
            return a+b

        self.assertEqual(add(1, 2), '3')

    def test_self(self):
        class Wtf(object):
            @typed('self', Number, Number, returns=Number)
            def add(self, a, b):
                return a + b

        Wtf().add(1, 2.5)



    def test_T2(self):
        @typed((int, None))
        def testa(a=5):
            pass

        self.assertRaises(TypeError, lambda: testa(2.0))
        testa(a=2.0)
        self.assertRaises(TypeError, lambda: testa('yuyu'))
        testa(a=None)
        testa(a=6)

    def test_T2a(self):
        @typed(Optional(int))
        def testa(a=5):
            pass

        self.assertRaises(TypeError, lambda: testa(2.0))
        testa(a=2.0)
        self.assertRaises(TypeError, lambda: testa('yuyu'))
        testa(a=None)
        testa(a=6)

    def test_t3(self):
        def a(b, c):
            pass

        def b(b, c):
            pass

        def c(b, c, **args):
            pass

        self.assertEquals(CallSignature(a), CallSignature(b))
        self.assertNotEquals(CallSignature(a), CallSignature(c))
