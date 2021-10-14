import struct
import unittest

from satella.exceptions import NotEnoughBytes
from satella.parsing import BinaryParser


class TestParsing(unittest.TestCase):
    def test_something(self):
        bp = BinaryParser(b'\x00\x00\x01\x02\x00\x00\x00\xFF\x00')
        self.assertEqual(bp.get_bytes(2), b'\x00\x00')
        self.assertEqual(bp.get_structs('BB'), (1, 2))
        self.assertEqual(bp.get_struct(struct.Struct('>L')), 255)
        self.assertRaises(NotEnoughBytes, lambda: bp.get_struct('>L'))
        self.assertRaises(NotEnoughBytes, lambda: bp.get_bytes(5))
        self.assertRaises(NotEnoughBytes, lambda: BinaryParser(b'', 1))
        self.assertEqual(bp.get_remaining_bytes(), b'\x00')
        self.assertEqual(len(bp), 1)
