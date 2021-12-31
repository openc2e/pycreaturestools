import struct


def read_exact(f, n):
    result = f.read(n)
    if len(result) != n:
        raise EOFError()
    return result


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


def write_u16le_many(f, values):
    write_all(f, struct.pack("<" + "H" * len(values), *values))


def write_u32le(f, value):
    write_all(f, struct.pack("<I", value))
