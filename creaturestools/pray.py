import io
import re
import string
import zlib

from creaturestools._io_utils import *
from creaturestools.exceptions import *

PRAY_TAG_BLOCK_TYPES = (
    "AGNT",  # C3 agent
    "DSAG",  # DS agent
    "MACH",  # SM agent
    "HAND",  # SM agent
    "LIVE",  # SM agent
    "MONK",  # SM agent
    "EXPC",  # C3 creature info
    "DSEX",  # DS creature info
    "SFAM",  # C3 starter family
    "EGGS",  # eggs
    "DFAM",  # DS starter family
    "warp",  # NetBabel warped creature info
    "CHAT",  # NetBabel chat message
    "REQU",  # NetBabel chat request
    "MESG",  # NetBabel
)


def _parse_tag_data(data):
    f = io.BytesIO(data)

    values = {}

    num_int_values = read_u32le(f)
    for _ in range(num_int_values):
        name = read_u32le_prefixed_string(f).decode("cp1252")
        if name in values:
            raise ReadError("Got duplicate tag name {!r}".format(name))
        value = read_u32le(f)
        values[name] = value

    num_str_values = read_u32le(f)
    for _ in range(num_str_values):
        name = read_u32le_prefixed_string(f).decode("cp1252")
        if name in values:
            raise ReadError("Got duplicate tag name {!r}".format(name))
        value = read_u32le_prefixed_string(f).decode("cp1252")
        values[name] = value

    return values


def iter_pray_file_raw(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        if not hasattr(f, "peek"):
            f = better_peekable_stream(f)

        magic = read_exact(f, 4)
        if magic != b"PRAY":
            raise ReadError(
                "Expected file magic to be b'PRAY', but got {}".format(magic)
            )

        while f.peek():
            block_type = read_exact(f, 4).decode("ascii")
            # TODO: validate it's ascii alphanumeric?
            block_name = read_exact(f, 128)
            nul_index = block_name.find(b"\x00")
            if block_name[nul_index:] != b"\x00" * (len(block_name) - nul_index):
                raise ReadError(
                    "Expected block name to end with nuls, but got {}".format(
                        block_name
                    )
                )
            block_name = block_name[:nul_index].decode("cp1252")

            length = read_u32le(f)
            length_decompressed = read_u32le(f)
            flags = read_u32le(f)
            if flags not in (0, 1):
                raise ReadError(
                    "Expected flags to be 0x0 (none) or 0x1 (compressed), but got {:x}".format(
                        flags
                    )
                )
            flag_compressed = flags & 1
            if (length != length_decompressed) != flag_compressed:
                raise ReadError(
                    "Expected compression flag {} to match length {} and length_decompressed {}".format(
                        compressed, length, length_decompressed
                    )
                )

            data = read_exact(f, length)

            yield block_type, block_name, length_decompressed, flag_compressed, data


def read_pray_file(fname_or_stream):
    blocks = []
    for (
        block_type,
        block_name,
        length_decompressed,
        flag_compressed,
        data,
    ) in iter_pray_file_raw(fname_or_stream):
        if flag_compressed:
            data = zlib.decompress(data)

        if len(data) != length_decompressed:
            raise ReadError(
                "Expected length of decompressed data to be {}, but got {}".format(
                    length_decompressed, len(data)
                )
            )

        if block_type in PRAY_TAG_BLOCK_TYPES:
            data = _parse_tag_data(data)

        blocks.append((block_type, block_name, data))
    return blocks


def _encode_pray_tags(data):
    out = io.BytesIO()

    int_tags = []
    str_tags = []
    for key, value in data.items():
        if isinstance(value, int):
            int_tags.append((key.encode("cp1252"), value))
        elif isinstance(value, str):
            str_tags.append((key.encode("cp1252"), value.encode("cp1252")))
        else:
            raise ValueError("Can't encode tag {!r} value {!r}".format(key, value))

    write_u32le(out, len(int_tags))
    for key, value in int_tags:
        write_u32le(out, len(key))
        write_all(out, key)
        write_u32le(out, value)

    write_u32le(out, len(str_tags))
    for key, value in str_tags:
        write_u32le(out, len(key))
        write_all(out, key)
        write_u32le(out, len(value))
        write_all(out, value)

    return bytes(out.getbuffer())


def write_pray_file(fname_or_stream, blocks, compression=zlib.Z_DEFAULT_COMPRESSION):
    with open_if_not_stream(fname_or_stream, "wb") as f:
        write_all(f, b"PRAY")

        for (block_type, block_name, data) in blocks:
            write_all(f, block_type.encode("ascii"))
            write_all(f, (block_name + (128 - len(block_name)) * "\0").encode("cp1252"))

            if isinstance(data, dict):
                data = _encode_pray_tags(data)
            if not isinstance(data, (bytes, memoryview)):
                raise ValueError(
                    "Can't write pray block data of type {!r}".format(data)
                )

            original_data_length = len(data)
            if compression:
                data = zlib.compress(data, level=compression)

            write_u32le(f, len(data))
            write_u32le(f, original_data_length)
            write_u32le(f, 1 if compression else 0)
            write_all(f, data)
