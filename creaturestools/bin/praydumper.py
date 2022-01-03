import argparse
import os
import sys

from creaturestools.pray import *
from creaturestools.sprites import *


def _replace_ext(fname, ext):
    return os.path.splitext(fname)[0] + ext


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument("file")
    opts.add_argument(
        "--convert-images",
        action="store_true",
        help="Convert sprites into .png files",
    )
    args = opts.parse_args()

    input_filename = args.file
    convert_images = args.convert_images
    filename_root = os.path.basename(os.path.splitext(input_filename)[0])
    output_directory = filename_root

    try:
        os.makedirs(output_directory)
    except FileExistsError:
        pass

    def filenamefilter(relative_filename, data):
        ext = os.path.splitext(relative_filename.lower())[1]
        if convert_images and ext in (".s16", ".c16", ".blk"):
            data = io.BytesIO(data)
            if ext == ".s16":
                image = stitch_to_sheet(read_s16_file(data))
            elif ext == ".c16":
                image = stitch_to_sheet(read_c16_file(data))
            elif ext == ".blk":
                image = read_blk_file(data)

            relative_filename = _replace_ext(relative_filename, ".png")
            output_filename = os.path.join(output_directory, relative_filename)
            print(f"Writing {output_filename}")
            image.save(output_filename)
            return relative_filename

        output_filename = os.path.join(output_directory, relative_filename)
        print(f"Writing {output_filename}")
        with open(output_filename, "wb") as f:
            f.write(data)
        return relative_filename

    blocks = read_pray_file(input_filename)

    pray_source = pray_to_pray_source(blocks, filenamefilter)

    output_filename = os.path.join(output_directory, filename_root + ".pray.txt")
    print(f"Writing {output_filename}")
    with open(output_filename, "wb") as f:
        f.write(pray_source.encode("utf-8"))  # I guess?


if __name__ == "__main__":
    main()
