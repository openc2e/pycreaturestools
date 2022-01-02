import sys

from PIL import Image

import creaturestools.sprites


def main():
    input_filename = sys.argv[1]

    with open(input_filename, "rb") as f:
        if input_filename.lower().endswith(".c16"):
            images = creaturestools.sprites.read_c16_file(f)
        elif input_filename.lower().endswith(".s16"):
            images = creaturestools.sprites.read_s16_file(f)
        elif input_filename.lower().endswith(".blk"):
            images = [creaturestools.sprites.read_blk_file(f)]
        elif input_filename.lower().endswith(".spr"):
            images = creaturestools.sprites.read_spr_file(f)
        else:
            raise Exception(
                "Don't know how to open filename '{}'".format(input_filename)
            )

    for i, img in enumerate(images):
        img.save("out{}.png".format(i))


if __name__ == "__main__":
    main()
