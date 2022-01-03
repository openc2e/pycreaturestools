import os
import sys
import zlib

from creaturestools.pray import *
from creaturestools.sprites import *


def _replace_ext(fname, ext):
    return os.path.splitext(fname)[0] + ext


def main():
    input_filename = sys.argv[1]
    output_filename_parts = os.path.basename(input_filename).split(".")
    output_filename_parts.insert(-1, "crushed")
    output_filename = ".".join(output_filename_parts)

    with open(output_filename, "wb") as out:
        original_size = 4
        out_size = 4
        write_all(out, b"PRAY")
        for (
            block_name,
            block_type,
            length_decompressed,
            flag_compressed,
            original_data,
        ) in iter_pray_file_raw(input_filename):
            original_size += 132 + 12 + len(original_data)
            if flag_compressed:
                uncompressed_data = zlib.decompress(original_data)
            else:
                uncompressed_data = original_data
            data = zlib.compress(uncompressed_data, 9)

            print(
                f"{block_name} {block_type} {len(original_data)} -> {len(data)} ({int(len(data) / len(original_data) * 100)}%)"
            )

            out_size += 132 + 12 + len(data)
            write_all(out, block_type.encode("ascii"))
            write_all(
                out, (block_name + " " * (128 - len(block_name))).encode("cp1252")
            )
            write_u32le(out, len(data))
            write_u32le(out, len(uncompressed_data))
            write_u32le(out, 1)
            write_all(out, data)

    print("")
    print(
        f"{output_filename} {original_size} -> {out_size} ({int(out_size / original_size * 100)}%)"
    )


if __name__ == "__main__":
    main()
