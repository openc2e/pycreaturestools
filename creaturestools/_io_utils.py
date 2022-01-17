import pathlib
import struct
from contextlib import contextmanager


@contextmanager
def _nullcontext(enter_result):
    # For Python 3.7, use contextlib._nullcontext
    yield enter_result


def open_if_not_stream(f, mode):
    if isinstance(f, (str, bytes, pathlib.Path)):
        return open(f, mode)
    else:
        return _nullcontext(f)


def read_entire_file(path):
    with open(path, "rb") as f:
        return f.read()


def peek_exact(f, n):
    result = f.peek(n)[:n]
    if len(result) != n:
        raise IOError("Expected to peek {} bytes, but got {}".format(n, len(result)))
    return result


def read_exact(f, n):
    result = f.read(n)
    if len(result) != n:
        raise EOFError("Expected to read {} bytes, but got {}".format(n, len(result)))
    return result


def read_u8(f):
    return struct.unpack("B", read_exact(f, 1))[0]


def read_u16le(f):
    return struct.unpack("<H", read_exact(f, 2))[0]


def read_u16be(f):
    return struct.unpack(">H", read_exact(f, 2))[0]


def read_u32le(f):
    return struct.unpack("<I", read_exact(f, 4))[0]


def read_u32be(f):
    return struct.unpack(">I", read_exact(f, 4))[0]


def read_s32le(f):
    return struct.unpack("<i", read_exact(f, 4))[0]


def read_null_terminated_string(r):
    s = b""
    while True:
        buf = read_exact(r, 1)
        if buf[0] == 0:
            break
        s += buf
    return s


def read_cstring(f):
    length = read_u8(f)
    if length == 0xFF:
        length = read_u16le(f)
    if length == 0xFFFF:
        length = read_u32le(f)
    if length == 0xFFFFFFFF:
        raise NotImplementedError("CString with length > 0xFFFFFFFF")
    return read_exact(f, length)


def read_u32le_prefixed_string(f):
    length = read_u32le(f)
    return read_exact(f, length)


def write_all(f, value):
    itemsize = getattr(value, "itemsize", 1)
    while value:
        n = f.write(value)
        assert n > 0
        assert n % itemsize == 0
        value = value[n // itemsize :]


def write_u16le(f, value):
    write_all(f, struct.pack("<H", value))


def write_many_u16le(f, values):
    write_all(f, struct.pack("<" + "H" * len(values), *values))


def write_u32le(f, value):
    write_all(f, struct.pack("<I", value))


def decode_creatures_string(s):
    if not isinstance(s, bytes):
        raise ValueError("Expected bytes, but got {!r}".format(s))

    if s[0:3] == b"\xef\xbb\xbf":
        return s[3:].decode("utf-8")
    if s[0:2] == b"\xff\xfe":
        return s[2:].decode("utf-16-le")
    if s[0:2] == b"\xfe\xff":
        return s[2:].decode("utf-16-be")

    try:
        return s.decode("utf-8")
    except DecodeError:
        # TODO: make sure it makes sense? some sort of character detection?
        return s.decode("cp1252")


class better_peekable_stream:
    """The peek() method on normal streams is not guaranteed to return as many
    bytes as requested, and in fact often returns less (for files, it seems to
    just return the internal FILE* buffer, whatever size that may be at the
    moment).

    This class wraps another stream and implements a peek() that always returns
    exactly the number of bytes requested."""

    def __init__(self, underlying_stream):
        self._peeked = b""
        self._underlying_stream = underlying_stream

    def read(self, n):
        result = b""
        if self._peeked:
            result += self._peeked[:n]
            self._peeked = self._peeked[n:]
        if len(result) < n:
            result += self._underlying_stream.read(n - len(result))
        return result

    def peek(self, n=1):
        while len(self._peeked) < n:
            read = self._underlying_stream.read(n - len(self._peeked))
            if len(read) == 0:
                break
            self._peeked += read
        return self._peeked[:n]
