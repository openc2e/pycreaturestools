import argparse
import os
import sys

import PIL.Image

from creaturestools._io_utils import *
from creaturestools._simplelexer import *
from creaturestools.caos2pray import *
from creaturestools.exceptions import *
from creaturestools.mngmusic import *
from creaturestools.pray import *
from creaturestools.praysource import *
from creaturestools.sprites import *


def _find_neighboring_file(filename, allowed_extensions):
    for neighbor in filename.parent.iterdir():
        for ext in allowed_extensions:
            if (
                str(neighbor).lower().endswith(ext)
                and str(neighbor.name)[: -len(ext)] == filename.stem
            ):
                return neighbor


def _cut_sheet_if_needed(image):
    colorkey = find_sprite_sheet_colorkey(image)
    if colorkey:
        return cut_sheet_to_sprites(image, colorkey=colorkey)
    else:
        return [image]


def _build_sprite(filename, ext):
    image = PIL.Image.open(filename).convert("RGB")
    b = io.BytesIO()
    if ext == ".c16":
        images = _cut_sheet_if_needed(image)
        write_c16_file(b, images)
    elif ext == ".s16":
        images = _cut_sheet_if_needed(image)
        write_s16_file(b, images)
    elif ext == ".blk":
        write_blk_file(b, image)
    else:
        raise ValueError(
            "Expected ext to be one '.blk', '.c16', or '.s16', but got {}", ext
        )
    return b.getbuffer()


def _build_music(filename):
    filename_dirname = os.path.dirname(filename)
    filename_root = os.path.basename(os.path.splitext(filename)[0])
    if filename_root.lower().endswith(".mng"):
        filename_root = filename_root[: -len(".mng")]

    with open(filename) as f:
        script = f.read()

    def mngfileloaderfunc(mngname):
        child_mngname = os.path.join(filename_dirname, filename_root, mngname)
        mngname = os.path.join(filename_dirname, mngname)
        if not os.path.exists(mngname) and os.path.exists(child_mngname):
            mngname = child_mngname
        print("Loading {!r}".format(mngname))
        with open(mngname, "rb") as f:
            return f.read()

    b = io.BytesIO()
    write_mng_file(b, script, mngfileloaderfunc)
    return b.getbuffer()


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument("file", type=pathlib.Path)
    opts.add_argument("--output-file")
    opts.add_argument(
        "--no-convert-images",
        dest="convert_images",
        action="store_false",
        help="Don't build sprites from .png/.bmp files",
    )
    opts.add_argument(
        "--no-convert-music",
        dest="convert_music",
        action="store_false",
        help="Don't build MNG music from .mng.txt/.wav files",
    )
    args = opts.parse_args()

    input_filename = args.file
    if args.output_file:
        output_filename = args.output_file
    else:
        output_filename = input_filename.stem  # removes one extension
        if output_filename.lower().endswith(".pray"):
            output_filename = output_filename[: -len(".pray")]
        output_filename += ".agents"
    input_dirname = os.path.dirname(input_filename)

    if input_filename.suffix.lower() == ".cos":
        blocks = parse_caos2pray_source_file(input_filename)
    else:
        blocks = parse_pray_source_file(input_filename)

    def fileloaderfunc(filename):
        original_filename = filename
        filename = input_dirname / pathlib.Path(filename)

        if filename.exists():
            return read_entire_file(filename)

        if args.convert_images and filename.suffix.lower() in (".blk", ".c16", ".s16"):
            neighbor = _find_neighboring_file(filename, (".bmp", ".png"))
            if neighbor:
                print("Building '{}' from '{}'".format(original_filename, neighbor))
                return _build_sprite(neighbor, filename.suffix.lower())

        if args.convert_music and filename.suffix.lower() == ".mng":
            neighbor = _find_neighboring_file(filename, (".mng.txt",))
            if neighbor:
                print("Building '{}' from '{}'".format(original_filename, neighbor))
                return _build_music(neighbor)

        raise FileNotFoundError(filename)

    for (block_type, block_name, data) in blocks:
        print(f'block {block_type} "{block_name}"')
    loadedblocks = pray_load_file_references(blocks, fileloaderfunc)

    print(f"Writing {output_filename}")
    write_pray_file(output_filename, loadedblocks)


if __name__ == "__main__":
    main()
