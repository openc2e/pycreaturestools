import argparse
import os
import re
import sys

import PIL.Image

from creaturestools.sprites import *


def _natural_sort_key(text):
    parts = [
        int(c) if c.isdigit() else c.lower() for c in re.split("([0-9]+)", text) if c
    ]
    if isinstance(parts[0], int):
        # keep a string integer string pattern
        parts.insert(0, "")
    return tuple(parts)


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument(
        "file",
        nargs="+",
        help="If a single file is given, assume it's a spritesheet. If multiple files are given, use each as one sprite.",
    )
    opts.add_argument("--output-filename")
    opts.add_argument(
        "--format", choices=["auto", "c16", "s16", "blk", "spr"], default="auto"
    )
    opts.add_argument(
        "--no-natural-sort", dest="natural_sort", action="store_false", default=True
    )
    args = opts.parse_args()

    input_filenames = args.file
    output_filename = args.output_filename
    format = args.format
    natural_sort = args.natural_sort

    if len(input_filenames) == 1 and format != "blk":
        # TODO: what if it's a BLK?
        print("Reading {} as spritesheet".format(input_filenames[0]))
        image = PIL.Image.open(input_filenames[0])
        # TODO: always necessary to convert to RGB? what if the palette looks fine?
        image = image.convert("RGB")
        colorkey = find_sprite_sheet_colorkey(image)
        if not colorkey:
            raise Exception(
                "Couldn't find spritesheet colorkey: the top-left 5x5 area needs to be a solid, non-black color."
            )
        images = cut_sheet_to_sprites(image, colorkey=colorkey)
        print("Found {} sprites".format(len(images)))
    else:
        images = []

        if natural_sort:
            sorted_filenames = sorted(input_filenames, key=_natural_sort_key)
            if sorted_filenames != input_filenames:
                print(
                    "WARNING: Input filenames were not in natural sort order (e.g. input1.png, input10.png, input2.png...)"
                )
                print(
                    "WARNING: Treating filenames as though they were given in natural sort order (e.g. input1.png, input2.png, input10.png...)"
                )
                print(
                    "WARNING: If you don't want this behavior, then call this program with: --no-natural-sort"
                )
                input_filenames = sorted_filenames

        for _ in input_filenames:
            print("Reading {}".format(_))
            images.append(PIL.Image.open(_))

    if format == "auto":
        if images[0].mode == "P":
            print("Using output format SPR because input images are paletted")
            format = "spr"
        else:
            print("Using output format C16")
            format = "c16"
        # TODO: make BLKs if it's a giant single image?
    else:
        print("Using output format {}".format(format.capitalize()))

    if not output_filename:
        base_filename = os.path.splitext(os.path.basename(input_filenames[0]))[0]
        output_filename = "{}.{}".format(base_filename, format)

    print("Writing {}".format(output_filename))
    write_c16_file(output_filename, images)


if __name__ == "__main__":
    main()
