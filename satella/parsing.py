import struct
import typing as tp

from satella.exceptions import NotEnoughBytes


class BinaryParser:
    """
    A class that allows parsing binary streams easily.

    This supports __len__ to return the amount of bytes remaining.

    :param b_stream: an object that allows indiced access, and allows subscripts to
        span ranges, which will return items parseable by struct
    :param offset: initial offset into the stream
    :raises NotEnoughBytes: offset larger than stream length

    :ivar offset: offset from which bytes will be readed
    """
    def __len__(self) -> int:
        return self.get_remaining_bytes_count()

    def get_remaining_bytes_count(self) -> int:
        """
        Return the amount of bytes remaining. This will not advance the pointer
        """
        return self.stream_length - self.pointer

    def __init__(self, b_stream: tp.Union[bytes, bytearray], offset: int = 0):
        self.b_stream = b_stream
        self.struct_cache = {}
        self.stream_length = len(b_stream)
        self.pointer = offset
        if offset > len(self.b_stream):
            raise NotEnoughBytes('Offset larger than the stream!')

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
        if self.stream_length < self.pointer + n:
            raise NotEnoughBytes('Not enough bytes')
        try:
            return self.b_stream[self.pointer:self.pointer+n]
        finally:
            self.pointer += n

    def get_struct(self, st: tp.Union[str, struct.Struct]) -> tp.Union[int, float]:
        """
        Try to obtain as many bytes as this struct requires and return them parsed.

        This must be a single-character struct!

        This will advance the pointer by size of st.

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
        if self.stream_length < self.pointer + st_len:
            raise NotEnoughBytes('Not enough bytes')

        try:
            return st.unpack(self.b_stream[self.pointer:self.pointer+st_len])[0]
        finally:
            self.pointer += st_len

    def get_structs(self, st: tp.Union[str, struct.Struct]) -> tp.Tuple[tp.Union[int, float],
                                                                        ...]:
        """
        Try to obtain as many bytes as this struct requires and return them parsed.

        This will advance the pointer by size of st.

        :param st: a struct.Struct or a multi character struct specification
        :return: a tuple of un-parsed values
        :raises NotEnoughBytes: not enough bytes remain in the stream!
        """
        st = self._to_struct(st)
        st_len = st.size
        if self.stream_length < self.pointer + st_len:
            raise NotEnoughBytes('Not enough bytes')
        try:
            return st.unpack(self.b_stream[self.pointer:self.pointer+st_len])
        finally:
            self.pointer += st_len

    def get_remaining_bytes(self) -> tp.Union[bytes, bytearray]:
        """
        Return the remaining bytes.

        This will not advance the pointer
        """
        return self.b_stream[self.pointer:]
