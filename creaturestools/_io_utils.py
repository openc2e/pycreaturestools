import struct
from contextlib import contextmanager


@contextmanager
def _nullcontext(enter_result):
    # For Python 3.7, use contextlib._nullcontext
    yield enter_result


def open_if_not_stream(f, mode):
    if isinstance(f, (str, bytes)):
        return open(f, mode)
    else:
        return _nullcontext(f)


def read_exact(f, n):
    result = f.read(n)
    if len(result) != n:
        raise EOFError()
    return result


def read_u8(f):
    return struct.unpack("B", read_exact(f, 1))[0]


def read_u16le(f):
    return struct.unpack("<H", read_exact(f, 2))[0]


def read_u32le(f):
    return struct.unpack("<I", read_exact(f, 4))[0]


def write_all(f, value):
    while value:
        n = f.write(value)
        assert n > 0
        value = value[n:]


def write_u16le(f, value):
    write_all(f, struct.pack("<H", value))


def write_many_u16le(f, values):
    write_all(f, struct.pack("<" + "H" * len(values), *values))


def write_u32le(f, value):
    write_all(f, struct.pack("<I", value))
