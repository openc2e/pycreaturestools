import os
import sys

from PIL import Image

import creaturestools.sprites


def stitch_to_sheet(images):
    if not all(_.mode == images[0].mode for _ in images):
        raise ValueError(
            "All images must be in the same color mode to stich to a sheet"
        )

    SHEET_PADDING = 5
    max_width = 800
    total_width = 0
    total_height = 0

    # find good row size
    current_row_width = SHEET_PADDING
    current_row_height = 0
    for i in images:
        if current_row_width + i.width + SHEET_PADDING > max_width:
            total_height += current_row_height + SHEET_PADDING
            current_row_width = SHEET_PADDING
            current_row_height = 0
        current_row_width += i.width + SHEET_PADDING
        current_row_height = max(current_row_height, i.height)
        total_width = max(total_width, current_row_width)
    total_height += SHEET_PADDING + current_row_height + SHEET_PADDING

    # set up storage, set to default background color
    newimage = Image.new(images[0].mode, size=(total_width, total_height))
    if newimage.mode == "P":
        # 0x1C,0x29,0x3B in C1 palette.dta -> rgb(112, 164, 236)
        newimage.paste(100, (0, 0, newimage.width, newimage.height))
        newimage.putpalette(images[0].getpalette())
    else:
        newimage.paste((112, 164, 236), (0, 0, newimage.width, newimage.height))

    # copy sprites over
    current_x = SHEET_PADDING
    current_y = SHEET_PADDING
    current_row_height = 0
    for i in images:
        # check row
        if current_x + i.width + SHEET_PADDING > total_width:
            current_y += current_row_height + SHEET_PADDING
            current_x = SHEET_PADDING
            current_row_height = 0
        # copy
        for y in range(i.height):
            newimage.paste(
                i, (current_x, current_y, current_x + i.width, current_y + i.height)
            )
        current_x += i.width + SHEET_PADDING
        current_row_height = max(current_row_height, i.height)

    return newimage


def main():
    input_filename = sys.argv[1]

    if input_filename.lower().endswith(".c16"):
        image = stitch_to_sheet(creaturestools.sprites.read_c16_file(input_filename))
    elif input_filename.lower().endswith(".s16"):
        image = stitch_to_sheet(creaturestools.sprites.read_s16_file(input_filename))
    elif input_filename.lower().endswith(".blk"):
        image = creaturestools.sprites.read_blk_file(input_filename)
    elif input_filename.lower().endswith(".spr"):
        image = stitch_to_sheet(creaturestools.sprites.read_spr_file(input_filename))
    else:
        raise Exception("Don't know how to open filename '{}'".format(input_filename))

    output_filename = os.path.splitext(os.path.basename(input_filename))[0] + ".png"
    print("Writing {}".format(output_filename))
    image.save(output_filename)


if __name__ == "__main__":
    main()
