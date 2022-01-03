import os
import sys

from PIL import Image

from creaturestools.sprites import *


def main():
    input_filename = sys.argv[1]

    if input_filename.lower().endswith(".c16"):
        image = stitch_to_sheet(read_c16_file(input_filename))
    elif input_filename.lower().endswith(".s16"):
        image = stitch_to_sheet(read_s16_file(input_filename))
    elif input_filename.lower().endswith(".blk"):
        image = read_blk_file(input_filename)
    elif input_filename.lower().endswith(".spr"):
        image = stitch_to_sheet(read_spr_file(input_filename))
    else:
        raise Exception("Don't know how to open filename '{}'".format(input_filename))

    output_filename = os.path.splitext(os.path.basename(input_filename))[0] + ".png"
    print("Writing {}".format(output_filename))
    image.save(output_filename)


if __name__ == "__main__":
    main()
