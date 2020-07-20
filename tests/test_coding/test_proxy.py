import math
import unittest

from satella.coding.structures import Proxy


class TestProxy(unittest.TestCase):
    def test_proxy(self):
        a = Proxy(5.25, True)
        self.assertIsInstance(a+2, Proxy)
        a = Proxy(5.25)
        self.assertNotIsInstance(a+2, Proxy)
        self.assertEqual(int(a), 5)
        self.assertEqual(float(a), 5.25)
        self.assertEqual(a - 0.25, 5.0)
        self.assertEqual(a * 2, 10.5)
        self.assertEqual(a / 2, 2.625)
        self.assertEqual(a // 2, 2)
        self.assertEqual(a ** 2, 5.25*5.25)
        self.assertEqual(-a, -5.25)
        self.assertEqual(math.floor(a), 5)
        self.assertEqual(divmod(a, 2), (2.0, 1.25))
        self.assertEqual(divmod(2, a), (0.0, 2.0))
        self.assertEqual(round(a), 5)
        self.assertEqual(math.trunc(a), 5)
        self.assertEqual(- 0.25+a, 5.0)
        self.assertEqual(2 * a, 10.5)
        self.assertEqual(2 / a, 2/5.25)
        self.assertEqual(2 // a, 0)
        self.assertEqual(complex(a), 5.25+0j)
        self.assertEqual(2 ** a,  2**5.25)
        a += 1.0
        self.assertEqual(a, 6.25)
        a -= 1.0
        self.assertEqual(a, 5.25)
        a *= 2.0
        self.assertEqual(a, 10.5)
        a /= 2.0
        self.assertEqual(a, 5.25)
        a //= 2.0
        self.assertEqual(a, 2.0)
        a = Proxy(2)
        self.assertEqual(str(a), '2')
        self.assertEqual(repr(a), '2')
        self.assertEqual(~a, -3)
        self.assertEqual(+a, 2)
        self.assertTrue(a < 3)
        self.assertTrue(a <= 3)
        self.assertFalse(a > 3)
        self.assertNotEqual(a, 3)
        self.assertFalse(a >= 3)
        self.assertEqual(a & 2, 2)
        self.assertEqual(a | 1, 3)
        self.assertEqual(2 ^ a, 0)
        self.assertEqual(a << 1, 4)
        self.assertEqual(a >> 1, 1)
        self.assertNotEqual(a, 6)
        self.assertEqual(2 & a, 2)
        self.assertEqual(1 | a, 3)
        self.assertEqual(1 << a, 4)
        self.assertEqual(1 >> a, 0)
        self.assertEqual(hex(a), '0x2')
        self.assertEqual(oct(a), '0o2')
        a <<= 2
        self.assertEqual(a, 8)
        a >>= 2
        self.assertEqual(a, 2)
        a |= 1
        self.assertEqual(a, 3)
        a &= 2
        self.assertEqual(a, 2)
        a ^= 2
        self.assertEqual(a, 0)
        a **= 2
        self.assertEqual(a, 0)

    def test_dict(self):
        a = Proxy(dict())
        a['test'] = 2
        self.assertEqual(['test'], list(iter(a)))
        self.assertIn('test', a)
        self.assertEqual(len(a), 1)
        self.assertEqual(a['test'], 2)
        del a['test']
        self.assertRaises(KeyError, lambda: a['test'])

    def test_class(self):
        class MyClass:
            def __init__(self, test):
                self.test = test

            def __matmul__(self, other):
                return 2

            def __rmatmul__(self, other):
                return 3

        a = Proxy(MyClass(2))
        self.assertEqual(a.test, 2)
        self.assertEqual(a @ 2, 2)
        self.assertEqual(2 @ a, 3)
        self.assertIn('test', dir(a))
        del a.test
        self.assertRaises(AttributeError, lambda: a.test)

