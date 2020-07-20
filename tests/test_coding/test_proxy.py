import math
import unittest

from satella.coding.structures import Proxy


class TestProxy(unittest.TestCase):
    def test_proxy(self):
        a = Proxy(5.25)
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
        self.assertEqual(2 ** a,  2**5.25)
        a = Proxy(2)
        self.assertEqual(a & 2, 2)
        self.assertEqual(a | 1, 3)
        self.assertEqual(a << 1, 4)
        self.assertEqual(a >> 1, 1)
        self.assertNotEqual(a, 6)
        self.assertEqual(2 & a, 2)
        self.assertEqual(1 | a, 3)
        self.assertEqual(1 << a, 4)
        self.assertEqual(1 >> a, 0)
        self.assertEqual(hex(a), '0x2')
        self.assertEqual(oct(a), '0o2')
