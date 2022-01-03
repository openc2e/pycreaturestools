# codec: utf-8

import struct
import sys

from creaturestools._io_utils import *
from creaturestools.cobs import _decode_c1_string


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("USAGE: {} filename".format(sys.argv[0]))

    filename = sys.argv[1]

    with open(filename, "rb") as f:
        num_items = read_u16le(f)
        print(f"{num_items=}")
        for i in range(num_items):
            print(f"item {i+1}")
            remaining_qty = read_u16le(f)
            print(f"{remaining_qty=}")
            script = read_cstring(f)
            print(f"{script=}")
            picture_width = read_u32le(f)
            print(f"{picture_width=}")
            picture_height = read_u32le(f)
            print(f"{picture_height=}")
            picture_width2 = read_u16le(f)
            print(f"{picture_width2=}")
            assert picture_width == picture_width2
            imagedata = f.read(picture_width * picture_height)
            image_name = _decode_c1_string(read_cstring(f))
            print(f"{image_name=}")
            image_description = _decode_c1_string(read_cstring(f))
            print(f"{image_description=}")


if __name__ == "__main__":
    main()
