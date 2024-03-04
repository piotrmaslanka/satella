from __future__ import absolute_import

import struct
import typing as tp

from satella.exceptions import NotEnoughBytes


class BinaryParser:
    """
    A class that allows parsing binary streams easily.

    This supports __len__ to return the amount of bytes in the stream,
    and __bytes__ to return the bytes.

    This is a zero-copy solution, and :meth:`get_parser` will be zero copy
    as well.

    :param b_stream: an object that allows subscripts to
        span ranges, which will return items parsable by struct
    :param offset: initial offset into the stream
    :param length: optional maximum length of byte count
    :raises NotEnoughBytes: offset larger than stream length

    :ivar pointer: pointer to the next bytes. Can be read and modified at will to
        preserve the earlier state of the BinaryParser.
    """

    def __len__(self) -> int:
        return self.length

    def get_remaining_bytes_count(self) -> int:
        """
        Return the amount of bytes remaining. This will not advance the pointer
        """
        return self.length - self.pointer + self.init_ofs

    def __init__(self, b_stream: tp.Union[bytes, bytearray], offset: int = 0,
                 length: tp.Optional[int] = None):
        self.b_stream = b_stream
        self.pointer = self.init_ofs = offset
        self.struct_cache = {}
        self.length = length or len(b_stream)
        if offset > len(self.b_stream):
            raise NotEnoughBytes('Offset larger than the stream!')

    def __bytes__(self) -> bytes:
        return self.b_stream[self.init_ofs:self.init_ofs + self.length]

    def skip(self, n: int) -> None:
        """
        Advance the pointer by n bytes

        :param n: bytes to advance
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        """
        self.assert_has_bytes(n)
        self.pointer += n

    def assert_has_bytes(self, n: int) -> None:
        """
        Assert that we have at least n bytes to consume.

        This does not advance the pointer.

        :param n: amount of bytes to consume
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        """
        if self.length + self.init_ofs < self.pointer + n:
            raise NotEnoughBytes('Not enough bytes')

    def get_parser(self, length: int) -> 'BinaryParser':
        """
        Return a subclassed binary parser providing a window to another binary parser's data.

        This will advance the pointer by length bytes

        :param length: amount of bytes to view
        :return: a BinaryParser
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        """
        self.assert_has_bytes(length)
        try:
            return BinaryParser(self.b_stream, self.pointer, length)
        finally:
            self.pointer += length

    def reset(self) -> None:
        """
        Reset the internal pointer to starting value
        :return:
        """
        self.pointer = self.init_ofs

    def _to_struct(self, st: tp.Union[str, struct.Struct]) -> struct.Struct:
        if isinstance(st, struct.Struct):
            return st
        else:
            if st in self.struct_cache:
                fmt = st
                return self.struct_cache[fmt]
            else:
                fmt = st
                st = struct.Struct(st)
                self.struct_cache[fmt] = st
                return st

    def get_bytes(self, n: int) -> bytes:
        """
        Return this many bytes

        :param n: amount of bytes to return
        :return: bytes returned
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        """
        self.assert_has_bytes(n)
        try:
            return self.b_stream[self.pointer:self.pointer + n]
        finally:
            self.pointer += n

    def get_struct(self, st: tp.Union[str, struct.Struct]) -> tp.Union[int, float]:
        """
        Try to obtain as many bytes as this struct requires and return them parsed.

        This must be a single-character struct!

        This will advance the pointer by size of st. Struct objects
        will be served from internal instance-specific cache.

        :param st: a single-character struct.Struct or a single character struct specification
        :return: a value returned from it
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        :raises AssertionError: struct was not a single element one!
        """
        st = self._to_struct(st)

        if st.format[0] in {'>', '<', '!', '@'}:
            assert len(st.format) == 2, 'Format must span at most 1 character, use ' \
                                        'get_structs for multiples!'
        else:
            assert len(st.format) == 1, 'Format must span at most 1 character, use ' \
                                        'get_structs for multiples!'

        st_len = st.size
        self.assert_has_bytes(st_len)
        try:
            return st.unpack(self.b_stream[self.pointer:self.pointer + st_len])[0]
        finally:
            self.pointer += st_len

    def get_structs(self, st: tp.Union[str, struct.Struct]) -> tp.Tuple[tp.Union[int, float],
                                                                        ...]:
        """
        Try to obtain as many bytes as this struct requires and return them parsed.

        This will advance the pointer by size of st. Struct objects
        will be served from internal instance-specific cache.

        :param st: a struct.Struct or a multi character struct specification
        :return: a tuple of un-parsed values
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        """
        st = self._to_struct(st)
        st_len = st.size
        self.assert_has_bytes(st_len)
        try:
            return st.unpack(self.b_stream[self.pointer:self.pointer + st_len])
        finally:
            self.pointer += st_len

    def get_remaining_bytes(self) -> tp.Union[bytes, bytearray]:
        """
        Return the remaining bytes.

        This will not advance the pointer
        """
        advance = self.pointer - self.init_ofs
        remaining = self.length - advance
        return self.b_stream[self.pointer:self.pointer + remaining]
