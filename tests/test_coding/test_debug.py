# coding=UTF-8
"""
It sounds like a melody
"""
from __future__ import print_function, absolute_import, division
import six
import unittest
from satella.coding.debug import typed


class TestTypecheck(unittest.TestCase):
    def test_t1(self):

        @typed(int, float, six.text_type)
        def testf(a_int, a_float, a_string):
            pass

        self.assertRaises(TypeError, lambda: testf('lol', 15, 'test'))
        self.assertRaises(TypeError, lambda: testf(12, 2.0, 'hey'))
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
