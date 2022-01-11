import argparse
import os

import PIL.Image

from creaturestools.sprites import *


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument("file")
    args = opts.parse_args()

    input_filename = args.file
    base_filename = os.path.splitext(os.path.basename(input_filename))[0]

    print("Reading {}".format(input_filename))
    image = PIL.Image.open(input_filename)
    colorkey = find_sprite_sheet_colorkey(image)
    if not colorkey:
        raise Exception(
            "Couldn't find colorkey: the top-left 5x5 area needs to be a solid, non-black color."
        )

    images = cut_sheet_to_sprites(image, colorkey=colorkey)
    for i, sprite in enumerate(images):
        output_filename = "{}-{}.png".format(base_filename, i)
        print("Writing {}".format(output_filename))
        sprite.save(output_filename)


if __name__ == "__main__":
    main()
