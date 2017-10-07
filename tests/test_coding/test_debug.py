# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding import typed, CallSignature


class TestTypecheck(unittest.TestCase):
    def test_cls(self):
        # if we don't care about apps
        class Lol(object):
            @typed(returns=int)
            def zomg(self, a):
                return a

        Lol().zomg(2)
        self.assertRaises(TypeError, lambda: Lol().zomg('a'))

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
            return a+b

        @typed(int, int, returns=str)
        def sum2(a, b):
            return a+b

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

        @typed((None, ))
        def testc(p):
            pass

        self.assertRaises(TypeError, lambda: testc(2))
        testc(None)

    def test_t2(self):

        @typed((int, None))
        def testa(a=5):
            pass

        self.assertRaises(TypeError, lambda: testa(2.0))
        testa(a=2.0)
        self.assertRaises(TypeError, lambda: testa('yuyu'))
        testa(a=None)
        testa(a=6)

    def test_self(self):

        class Wtf(object):
            @typed('self', int, int, returns=int)
            def add(self, a, b):
                return a+b

        Wtf().add(1,2)

    def test_T2(self):

        @typed((int, None))
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

