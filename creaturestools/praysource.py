import io
import pathlib
import re
import string

from ._io_utils import *
from ._simplelexer import *


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


def generate_pray_source(blocks, filenamefilter=lambda name, data: name):
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
            if isinstance(value, pathlib.Path):
                pray_source += f'"{_escape(key)}" @ "{_escape(str(value))}"\n'
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
        if isinstance(data, pathlib.Path):
            block_output_filename = str(data)
        else:
            block_output_filename = filenamefilter(block_name, data)
        pray_source += f'inline {block_type} "{_escape(block_name)}" "{_escape(block_output_filename)}"\n'

    return pray_source


def parse_pray_source_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        s = f.read()
    t = simplelexer(s)
    p = 0

    def _any_whitespace():
        nonlocal p
        while p < len(t) and t[p][0] in ("whitespace", "newline", "comment"):
            p += 1

    def _some_whitespace():
        if p < len(t) and t[p][0] not in ("whitespace", "newline", "comment"):
            raise Exception("Expected whitespace, but got {}".format(t[p]))
        _any_whitespace()

    # read encoding marker
    _any_whitespace()
    if p >= len(t) or t[p] != ("string", "en-GB"):
        raise Exception("Expected '\"en-GB\"', but got {}".format(t[p]))
    p += 1

    blocks = []

    while True:
        _any_whitespace()
        # check eoi
        if p >= len(t):
            break
        elif t[p][0] == "eoi":
            break
        # group block
        elif t[p] == ("word", "group"):
            p += 1
            _some_whitespace()

            # get block type
            if p >= len(t) or t[p][0] != "word" or len(t[p][1]) != 4:
                raise Exception(
                    "Expected 4-letter ASCII block type, but got {}".format(t)
                )
            block_type = t[p][1]
            p += 1
            _some_whitespace()

            # get block name
            if p >= len(t) or t[p][0] != "string":
                raise Exception("Expected block name, but got {}".format(t))
            block_name = t[p][1]
            p += 1
            _some_whitespace()

            tags = {}
            while True:
                # key name
                if p >= len(t):
                    break
                elif t[p][0] == "string":
                    key_name = t[p][1]
                else:
                    break
                p += 1
                _some_whitespace()

                # key value
                if p >= len(t):
                    raise Exception("Expected key value, got end-of-input")
                elif t[p][0] == "atsign":
                    p += 1
                    _some_whitespace()

                    if p >= len(t):
                        raise Exception("Expected key value, got end-of-input")
                    elif t[p][0] != "string":
                        raise Exception("Expected key value, got {}".format(t[p]))
                    else:
                        key_value = pathlib.Path(t[p][1])
                elif t[p][0] == "string":
                    key_value = t[p][1]
                elif t[p][0] == "integer":
                    key_value = int(t[p][1])
                else:
                    break
                p += 1
                _some_whitespace()

                tags[key_name] = key_value

            blocks.append((block_type, block_name, tags))

        # inline block
        elif t[p] == ("word", "inline"):
            p += 1
            _some_whitespace()

            # get block type
            if p >= len(t) or t[p][0] != "word" or len(t[p][1]) != 4:
                raise Exception(
                    "Expected 4-letter ASCII block type, but got {}".format(t)
                )
            block_type = t[p][1]
            p += 1
            _some_whitespace()

            # get block name
            if p >= len(t) or t[p][0] != "string":
                raise Exception("Expected block name, but got {}".format(t))
            block_name = t[p][1]
            p += 1
            _some_whitespace()

            # get inline source
            if p >= len(t) or t[p][0] != "string":
                raise Exception("Expected inline filename, but got {}".format(t))
            inline_filename = t[p][1]
            p += 1
            _some_whitespace()

            blocks.append((block_type, block_name, pathlib.Path(inline_filename)))

        # error
        else:
            raise Exception("Expected 'group' or 'inline', but got {}".format(t[p]))

    return blocks


def pray_load_file_references(blocks, fileloaderfunc):
    newblocks = []
    for block_type, block_name, data in blocks:
        if isinstance(data, pathlib.Path):
            newblocks.append((block_type, block_name, fileloaderfunc(data)))
        elif isinstance(data, dict):
            newdata = {}
            for key, value in data.items():
                if isinstance(value, pathlib.Path):
                    newdata[key] = decode_creatures_string(fileloaderfunc(value))
                else:
                    newdata[key] = value
            newblocks.append((block_type, block_name, newdata))
        else:
            newblocks.append((block_type, block_name, data))
    return newblocks
