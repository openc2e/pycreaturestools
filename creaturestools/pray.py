import io
import re
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


def _escape(s):
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _natural_sort_key(text):
    parts = [
        int(c) if c.isdigit() else c.lower() for c in re.split("([0-9]+)", text) if c
    ]
    if isinstance(parts[0], int):
        # keep a string integer string pattern
        parts.insert(0, "")
    return tuple(parts)


def _pray_sort_key(text):
    # keep Dependency and Dependency Category keys next to each other
    m = re.search("^Dependency Category (\d+)", text)
    if m:
        text = f"Dependency {m[1]} Category"
    # put Dependency Count before Dependencies
    if text == "Dependency Count":
        text = "Dependency 0 Count"
    # put Script Count before Script
    if text == "Script Count":
        text = "Script 0 Count"

    return _natural_sort_key(text)


def pray_to_pray_source(blocks, filenamefilter=lambda name, data: name):
    pray_source = ""
    pray_source += '"en-GB"\n\n'

    data_blocks = []
    for (block_type, block_name, data) in blocks:
        if isinstance(data, bytes):
            # save these for the end
            data_blocks.append((block_type, block_name, data))
            continue

        assert isinstance(data, dict)
        pray_source += f'group {block_type} "{_escape(block_name)}"\n'
        for key in sorted(data, key=_pray_sort_key):
            value = data[key]
            if isinstance(value, int):
                pray_source += f'"{_escape(key)}" {value}\n'
                continue

            assert isinstance(value, str)
            if key.startswith("Script ") and len(value) > 100:
                value = value.encode("utf-8")  # I guess?
                block_output_filename = filenamefilter(f"{block_name}_{key}.cos", value)
                pray_source += (
                    f'"{_escape(key)}" @ "{_escape(block_output_filename)}"\n'
                )
            else:
                pray_source += f'"{_escape(key)}" "{_escape(value)}"\n'
        pray_source += "\n"

    for (block_type, block_name, data) in sorted(
        data_blocks, key=lambda _: (_[0].lower(), _natural_sort_key(_[1]))
    ):
        block_output_filename = filenamefilter(block_name, data)
        pray_source += f'inline {block_type} "{_escape(block_name)}" "{_escape(block_output_filename)}"\n'

    return pray_source
