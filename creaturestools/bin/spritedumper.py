import argparse
import os
import sys

from PIL import Image

from creaturestools.creatures0 import *
from creaturestools.sprites import *


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument("file", nargs="+")
    opts.add_argument("--palette", help="Use a non-default palette.dta file")
    args = opts.parse_args()

    input_filenames = args.file
    palette = None
    if args.palette:
        palette = read_palette_dta_file(args.palette)

    creatures0_background_pieces = {}
    for fname in input_filenames:
        print("Reading {}".format(fname))
        if fname.lower().endswith(".c16"):
            image = stitch_to_sheet(read_c16_file(fname))
        elif fname.lower().endswith(".s16"):
            image = stitch_to_sheet(read_s16_file(fname))
        elif fname.lower().endswith(".blk"):
            image = read_blk_file(fname)
        elif fname.lower().endswith(".spr"):
            if is_creatures0_sprite_file(fname):
                images = read_creatures0_spr_file(fname, palette=palette)
                if (
                    os.path.basename(fname.upper())
                    in CREATURES0_SPRITE_BACKGROUND_PIECE_NAMES
                ):
                    if is_creatures0_sprite_background_piece(images):
                        creatures0_background_pieces[
                            os.path.basename(fname.upper())
                        ] = images[0]
                        continue
                    else:
                        print(
                            "Warning: expected {} to be a background piece, but doesn't seem like one".format(
                                fname
                            )
                        )
            else:
                images = read_spr_file(fname, palette=palette)
            image = stitch_to_sheet(images)
        else:
            raise Exception("Don't know how to open filename '{}'".format(fname))

        output_filename = os.path.splitext(os.path.basename(fname))[0] + ".png"
        print("Writing {}".format(output_filename))
        image.save(output_filename)

    if len(creatures0_background_pieces) == 128:
        # try to piece together the background!
        print("Got 128 background pieces, stitching them together")
        pieces_in_order = []
        for fname in CREATURES0_SPRITE_BACKGROUND_PIECE_NAMES:
            pieces_in_order.append(creatures0_background_pieces[fname])

        background = stitch_creatures0_sprite_background(pieces_in_order)
        output_filename = "background.png"
        print("Writing {}".format(output_filename))
        background.save(output_filename)
    elif creatures0_background_pieces:
        # eh, just write them out
        print(
            "Got {} background pieces, but expected 128".format(
                len(creatures0_background_pieces)
            )
        )
        for fname, image in creatures0_background_pieces.values():
            output_filename = "{}.png".format(os.path.splitext(fname.lower())[0])
            print("Writing {}".format(output_filename))
            image.save(output_filename)


if __name__ == "__main__":
    main()
