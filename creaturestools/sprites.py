import array
import io
import struct
import sys

from PIL import Image
from PIL.ImagePalette import ImagePalette

from ._image_utils import *
from ._io_utils import *
from .exceptions import *

CREATURES1_PALETTE = ImagePalette(
    palette=[
        # fmt: off
    0x00,0x00,0x00, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC,
    0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0x10,0x08,0x08,
    0x14,0x18,0x28, 0x18,0x28,0x10, 0x18,0x24,0x30, 0x2C,0x10,0x08, 0x28,0x18,0x24, 0x34,0x28,0x10,
    0x30,0x2C,0x30, 0x18,0x1C,0x44, 0x14,0x34,0x54, 0x18,0x3C,0x60, 0x24,0x1C,0x44, 0x2C,0x34,0x48,
    0x2C,0x38,0x68, 0x1C,0x40,0x1C, 0x1C,0x40,0x28, 0x34,0x48,0x18, 0x34,0x48,0x2C, 0x3C,0x60,0x18,
    0x3C,0x60,0x28, 0x18,0x40,0x5C, 0x1C,0x40,0x64, 0x34,0x44,0x50, 0x2C,0x4C,0x68, 0x38,0x60,0x4C,
    0x3C,0x60,0x70, 0x48,0x18,0x08, 0x48,0x1C,0x24, 0x50,0x2C,0x10, 0x48,0x34,0x2C, 0x68,0x18,0x0C,
    0x6C,0x1C,0x24, 0x6C,0x30,0x10, 0x68,0x34,0x24, 0x48,0x38,0x48, 0x48,0x38,0x68, 0x68,0x34,0x48,
    0x74,0x34,0x68, 0x50,0x48,0x14, 0x50,0x48,0x30, 0x50,0x64,0x18, 0x4C,0x68,0x2C, 0x70,0x48,0x14,
    0x6C,0x4C,0x2C, 0x70,0x64,0x14, 0x74,0x64,0x30, 0x4C,0x4C,0x4C, 0x4C,0x54,0x6C, 0x54,0x64,0x50,
    0x54,0x64,0x70, 0x68,0x54,0x4C, 0x68,0x58,0x68, 0x70,0x68,0x50, 0x6C,0x6C,0x6C, 0x30,0x3C,0x84,
    0x38,0x5C,0x90, 0x40,0x3C,0x84, 0x4C,0x58,0x8C, 0x48,0x58,0xB0, 0x50,0x68,0x8C, 0x48,0x6C,0xAC,
    0x64,0x58,0x88, 0x64,0x5C,0xAC, 0x6C,0x70,0x8C, 0x6C,0x74,0xA8, 0x4C,0x5C,0xC4, 0x50,0x74,0xC8,
    0x5C,0x70,0xEC, 0x68,0x78,0xCC, 0x64,0x78,0xF4, 0x68,0x8C,0x34, 0x5C,0x84,0x4C, 0x5C,0x80,0x68,
    0x6C,0x8C,0x4C, 0x74,0x88,0x70, 0x78,0xA4,0x4C, 0x78,0xA4,0x68, 0x58,0x80,0x8C, 0x5C,0x80,0xB8,
    0x70,0x84,0x94, 0x74,0x88,0xAC, 0x7C,0xA4,0x8C, 0x78,0xA4,0xB0, 0x58,0x84,0xCC, 0x58,0x90,0xE4,
    0x58,0xA4,0xF0, 0x70,0x88,0xCC, 0x74,0x88,0xFC, 0x78,0xA0,0xD8, 0x70,0xA4,0xEC, 0x8C,0x18,0x10,
    0x90,0x1C,0x24, 0x88,0x34,0x10, 0x8C,0x34,0x28, 0xAC,0x18,0x10, 0xAC,0x1C,0x20, 0xA8,0x30,0x10,
    0xAC,0x30,0x28, 0x98,0x34,0x48, 0x8C,0x4C,0x14, 0x8C,0x50,0x28, 0x90,0x68,0x14, 0x90,0x68,0x30,
    0xAC,0x50,0x14, 0xA8,0x54,0x28, 0xB0,0x68,0x14, 0xAC,0x6C,0x2C, 0x88,0x54,0x48, 0x88,0x58,0x6C,
    0x8C,0x6C,0x4C, 0x88,0x74,0x6C, 0xAC,0x50,0x48, 0xB0,0x54,0x64, 0xA8,0x74,0x48, 0xAC,0x74,0x68,
    0xD0,0x2C,0x1C, 0xD4,0x34,0x48, 0xC8,0x54,0x14, 0xC8,0x54,0x28, 0xCC,0x68,0x14, 0xCC,0x70,0x2C,
    0xE8,0x50,0x14, 0xE8,0x50,0x2C, 0xE8,0x74,0x14, 0xE8,0x74,0x28, 0xCC,0x50,0x48, 0xCC,0x54,0x64,
    0xCC,0x74,0x48, 0xC8,0x74,0x68, 0xE8,0x50,0x50, 0xEC,0x58,0x60, 0xF0,0x70,0x48, 0xEC,0x70,0x70,
    0x90,0x3C,0x84, 0x8C,0x50,0x84, 0x84,0x78,0x90, 0x84,0x78,0xA8, 0xA8,0x78,0x88, 0xA4,0x7C,0xA4,
    0x80,0x7C,0xC4, 0xD0,0x30,0x80, 0xD8,0x70,0x88, 0xEC,0x74,0xCC, 0xA4,0x88,0x2C, 0x94,0x84,0x50,
    0x90,0x88,0x70, 0x88,0xAC,0x50, 0x8C,0xAC,0x6C, 0xB0,0x88,0x50, 0xAC,0x8C,0x6C, 0xB4,0xA4,0x50,
    0xB4,0xA8,0x70, 0x9C,0xC4,0x3C, 0xA4,0xD0,0x5C, 0xD0,0x88,0x18, 0xD0,0x88,0x30, 0xD4,0xA8,0x14,
    0xD0,0xA8,0x2C, 0xF0,0x8C,0x14, 0xEC,0x8C,0x2C, 0xF4,0xAC,0x14, 0xF4,0xAC,0x30, 0xCC,0x8C,0x4C,
    0xC8,0x94,0x68, 0xD0,0xA8,0x50, 0xD0,0xA8,0x70, 0xEC,0x90,0x48, 0xEC,0x90,0x64, 0xF0,0xAC,0x4C,
    0xEC,0xB0,0x6C, 0xD0,0xC4,0x38, 0xF4,0xCC,0x0C, 0xF8,0xCC,0x30, 0xFC,0xF0,0x0C, 0xFC,0xEC,0x2C,
    0xD4,0xC4,0x50, 0xD4,0xC4,0x70, 0xC8,0xF4,0x50, 0xCC,0xF4,0x6C, 0xF8,0xC8,0x4C, 0xF4,0xCC,0x6C,
    0xF8,0xEC,0x4C, 0xFC,0xE8,0x70, 0x8C,0x88,0x90, 0x8C,0x90,0xAC, 0x90,0xA8,0x90, 0x94,0xA8,0xB4,
    0xA8,0x90,0x8C, 0xA4,0x98,0xB0, 0xB0,0xA8,0x90, 0xAC,0xA8,0xB4, 0x88,0x94,0xCC, 0x84,0x98,0xF8,
    0x94,0xA4,0xD0, 0x90,0xA8,0xFC, 0xA0,0x9C,0xC4, 0xAC,0xAC,0xCC, 0xA4,0xB8,0xF4, 0xA8,0xC8,0xA8,
    0x98,0xC4,0xC4, 0xB0,0xC0,0xD0, 0xA8,0xC4,0xFC, 0xB0,0xE8,0xC4, 0xB8,0xE4,0xE8, 0xCC,0x90,0x90,
    0xC8,0x98,0xA4, 0xCC,0xB0,0x8C, 0xC8,0xB0,0xB0, 0xEC,0x90,0x8C, 0xEC,0x90,0xA4, 0xE8,0xB4,0x88,
    0xE8,0xB4,0xA8, 0xC4,0xB8,0xC8, 0xC4,0xBC,0xE0, 0xF4,0xAC,0xCC, 0xD4,0xC8,0x90, 0xD0,0xC8,0xB0,
    0xCC,0xF0,0x88, 0xCC,0xE4,0xB0, 0xF0,0xCC,0x90, 0xEC,0xD0,0xAC, 0xF8,0xE8,0x90, 0xF8,0xEC,0xB0,
    0xD4,0xC8,0xCC, 0xC8,0xC8,0xE8, 0xD4,0xE4,0xCC, 0xD8,0xE8,0xE4, 0xE4,0xD4,0xD0, 0xE0,0xD0,0xE0,
    0xF0,0xE8,0xD0, 0xF4,0xF4,0xEC, 0xFC,0xFC,0xFC, 0x00,0x00,0x00, 0x00,0x00,0x00, 0x00,0x00,0x00,
    0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC,
    0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC, 0xFC,0xFC,0xFC,
        # fmt: on
    ]
)


def read_palette_dta_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        palette = []
        for _ in range(256 * 3):
            palette.append(read_u8(f) * 4)
        if f.peek():
            raise ReadError("Expected end-of-file, but got more data")
        return ImagePalette(palette=palette)


def read_s16_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        pixel_fmt = read_u32le(f)
        if pixel_fmt == 0:
            rawmode = "BGR;15"
        elif pixel_fmt == 1:
            rawmode = "BGR;16"
        else:
            desc = "Expected pixel format to be 0x0 (RGB555) or 0x1 (RGB565), but got 0x{:x}".format(
                pixel_fmt
            )
            if pixel_fmt == 2:
                desc += " (C16 RGB555)"
            elif pixel_fmt == 3:
                desc += " (C16 RGB565)"
            elif pixel_fmt == 0x1000000:
                desc += " (big-endian N16)"
            elif pixel_fmt == 0x3000000:
                desc += " (big-endian M16)"
            raise ReadError(desc)

        num_images = read_u16le(f)
        widths = []
        heights = []
        next_offset = 6 + (8 * num_images)
        for _ in range(num_images):
            offset = read_u32le(f)
            if offset != next_offset:
                raise ReadError(
                    "Expected image offset to be {}, but got {}".format(
                        next_offset, offset
                    )
                )
            widths.append(read_u16le(f))
            heights.append(read_u16le(f))
            next_offset += 2 * widths[-1] * heights[-1]

        if (
            num_images == 928
            and all(_ == 144 for _ in widths)
            and all(_ == 150 for _ in heights)
        ):
            # this is a background, not a normal sprite file
            width_blocks = 58
            height_blocks = 16
            totalwidth = 8352
            totalheight = 2400

            data = bytearray(totalwidth * totalheight * 2)
            for i in range(num_images):
                y = i % height_blocks
                x = i // height_blocks
                for blocky in range(150):
                    start = (y * 150 + blocky) * totalwidth * 2 + x * 144 * 2
                    data[start : start + 144 * 2] = read_exact(f, 144 * 2)

            image = Image.frombytes(
                "RGB",
                (totalwidth, totalheight),
                bytes(data),
                "raw",
                rawmode,
            )
            return [image]
        else:
            images = []
            for i in range(num_images):
                image = Image.frombytes(
                    "RGB",
                    (widths[i], heights[i]),
                    read_exact(f, 2 * widths[i] * heights[i]),
                    "raw",
                    rawmode,
                )
                image.info["rawmode"] = rawmode
                images.append(image)

            return images


def read_c16_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        pixel_fmt = read_u32le(f)
        if pixel_fmt == 2:
            rawmode = "BGR;15"
        elif pixel_fmt == 3:
            rawmode = "BGR;16"
        elif pixel_fmt == 0x3000000:
            raise NotImplementedError("Pixel format 0x3000000 (big-endian M16)")
        else:
            desc = "Expected pixel format to be 0x2 (RGB555) or 0x3 (RGB565), but got 0x{:x}".format(
                pixel_fmt
            )
            if pixel_fmt == 0:
                desc += " (S16 RGB555)"
            elif pixel_fmt == 1:
                desc += " (S16 RGB565)"
            elif pixel_fmt == 0x1000000:
                desc += " (big-endian N16)"
            raise ReadError(desc)

        num_images = read_u16le(f)
        offsets = []
        widths = []
        heights = []
        for i in range(num_images):
            line_offsets = [read_u32le(f)]
            widths.append(read_u16le(f))
            heights.append(read_u16le(f))
            for j in range(heights[i] - 1):
                line_offsets.append(read_u32le(f))
            offsets.append(line_offsets)

        images = []
        for i in range(num_images):
            # TODO: check offsets are correct
            # TODO: use array module instead
            data = bytearray(widths[i] * heights[i] * 2)
            for j in range(heights[i]):
                p = 0
                while p < widths[i]:
                    rle_tag = read_u16le(f)
                    is_color = rle_tag & 0x1
                    run_length = rle_tag >> 1
                    if p + run_length > widths[i]:
                        raise ReadError(
                            "Got run_length {}, which would result in an overwide line of {}".format(
                                run_length, p + run_length
                            )
                        )
                    if is_color:
                        data[
                            (j * widths[i] + p)
                            * 2 : (j * widths[i] + p + run_length)
                            * 2
                        ] = read_exact(f, run_length * 2)
                    else:
                        # bytearray() initializes memory to zero, so we don't need to do anything
                        pass
                    p += run_length

                end_of_line = read_u16le(f)
                if end_of_line != 0:
                    raise ReadError(
                        "Expected end-of-line byte to be 0, but got {}".format(
                            end_of_line
                        )
                    )
            end_of_image = read_u16le(f)
            if end_of_image != 0:
                raise ReadError(
                    "Expected end-of-image byte to be 0, but got {}".format(
                        end_of_image
                    )
                )
            image = Image.frombytes(
                "RGB", (widths[i], heights[i]), bytes(data), "raw", rawmode
            )
            image.info["rawmode"] = rawmode
            images.append(image)

        return images


def read_blk_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        pixel_fmt = read_u32le(f)
        if pixel_fmt == 0:
            rawmode = "BGR;15"
        elif pixel_fmt == 1:
            rawmode = "BGR;16"
        elif pixel_fmt == 0x1000000:
            raise NotImplementedError("Pixel format 0x1000000 (big-endian BLK)")
        else:
            desc = "Expected pixel format to be 0x0 (RGB555) or 0x1 (RGB565), but got 0x{:x}".format(
                pixel_fmt
            )
            raise ReadError(desc)

        width_blocks = read_u16le(f)
        height_blocks = read_u16le(f)
        num_images = read_u16le(f)

        if num_images != width_blocks * height_blocks:
            raise ReadError(
                "Expected {} x {} = {} sprites, but got {}".format(
                    width_blocks,
                    height_blocks,
                    width_blocks * height_blocks,
                    num_images,
                )
            )

        offsets = []
        next_offset = 10 + 8 * num_images
        for _ in range(num_images):
            offsets.append(read_u32le(f) + 4)
            if offsets[-1] != next_offset:
                raise ReadError(
                    "Expected image offset to be {}, but got {}".format(
                        next_offset, offsets[i]
                    )
                )
            width = read_u16le(f)
            height = read_u16le(f)
            if width != 128 or height != 128:
                raise ReadError(
                    "Expected image size to be 128x128, but got {}x{}".format(
                        width, height
                    )
                )
            next_offset += 2 * 128 * 128

        totalwidth = width_blocks * 128
        totalheight = height_blocks * 128

        data = bytearray(totalwidth * totalheight * 2)
        for i in range(num_images):
            y = i % height_blocks
            x = i // height_blocks
            for blocky in range(128):
                start = (y * 128 + blocky) * totalwidth * 2 + x * 128 * 2
                data[start : start + 128 * 2] = read_exact(f, 128 * 2)

        image = Image.frombytes(
            "RGB",
            (totalwidth, totalheight),
            bytes(data),
            "raw",
            rawmode,
        )
        image.info["rawmode"] = rawmode
        return image


def read_spr_file(fname_or_stream, palette=None):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        num_images = read_u16le(f)
        next_offset = 2 + 8 * num_images
        widths = []
        heights = []
        for _ in range(num_images):
            offset = read_u32le(f)
            if offset != next_offset:
                raise ReadError(
                    "Expected image offset to be {}, but got {}".format(
                        next_offset, offset
                    )
                )
            widths.append(read_u16le(f))
            heights.append(read_u16le(f))
            next_offset += widths[-1] * heights[-1]

        if (
            num_images == 464
            and all(_ == 144 for _ in widths)
            and all(_ == 150 for _ in heights)
        ):
            # this is a background, not a normal sprite file
            width_blocks = 58
            height_blocks = 8
            totalwidth = 8352
            totalheight = 1200

            data = bytearray(totalwidth * totalheight)
            for i in range(num_images):
                y = i % height_blocks
                x = i // height_blocks
                for blocky in range(150):
                    start = (y * 150 + blocky) * totalwidth + x * 144
                    data[start : start + 144] = read_exact(f, 144)

            image = Image.frombytes(
                "P",
                (totalwidth, totalheight),
                bytes(data),
            )
            image.putpalette(palette or CREATURES1_PALETTE)
            return [image]
        else:
            images = []
            for i in range(num_images):
                data = read_exact(f, widths[i] * heights[i])
                image = Image.frombytes(
                    "P",
                    (widths[i], heights[i]),
                    data,
                )
                # TODO: are all blacks transparent? or just palette index 0?
                image.putpalette(palette or CREATURES1_PALETTE)
                images.append(image)

            return images


def write_spr_file(fname_or_stream, images):
    with open_if_not_stream(fname_or_stream, "wb") as f:
        images = [
            convert_image(img, "P", palette=CREATURES1_PALETTE)
            if img.getpalette() != CREATURES1_PALETTE
            else img
            for img in images
        ]

        if len(images) == 1 and images[0].width == 8352 and images[0].height == 1200:
            # this is a background, not a normal sprite file
            img = images[0]
            num_images = 464
            width_blocks = 58
            height_blocks = 8
            sprwidth = 144
            sprheight = 150
            write_u16le(f, num_images)
            for i in range(num_images):
                write_u32le(f, 2 + 8 * num_images + sprwidth * sprheight * i)  # offset
                write_u16le(f, sprwidth)  # width
                write_u16le(f, sprheight)  # height

            data = img.tobytes()
            for i in range(num_images):
                y = i % height_blocks
                x = i // height_blocks
                for blocky in range(sprheight):
                    start = (y * sprheight + blocky) * img.width + x * sprwidth
                    write_all(f, data[start : start + sprwidth])
        else:
            write_u16le(f, len(images))
            next_offset = 2 + 8 * len(images)
            for img in images:
                write_u32le(f, next_offset)
                write_u16le(f, img.width)
                write_u16le(f, img.height)
                next_offset += img.width * img.height

            for img in images:
                write_all(f, img.tobytes())


def write_s16_file(fname_or_stream, images, pixel_fmt="RGB565"):
    if pixel_fmt not in ("RGB555", "RGB565"):
        raise ValueError("pixel_fmt must be either 'RGB565' or 'RGB555'")

    with open_if_not_stream(fname_or_stream, "wb") as f:
        if pixel_fmt == "RGB555":
            rawmode = "BGR;15"
            write_u32le(f, 0)
        elif pixel_fmt == "RGB565":
            rawmode = "BGR;16"
            write_u32le(f, 1)

        if len(images) == 1 and images[0].width == 8352 and images[0].height == 2400:
            # this is a background, not a normal sprite file
            img = images[0]
            num_images = 928
            width_blocks = 58
            height_blocks = 16
            sprwidth = 144
            sprheight = 150
            write_u16le(f, num_images)
            for i in range(num_images):
                write_u32le(
                    f, 6 + 8 * num_images + sprwidth * sprheight * 2 * i
                )  # offset
                write_u16le(f, sprwidth)  # width
                write_u16le(f, sprheight)  # height

            data = convert_image(img, rawmode).tobytes()
            for i in range(num_images):
                y = i % height_blocks
                x = i // height_blocks
                for blocky in range(sprheight):
                    start = (y * sprheight + blocky) * img.width * 2 + x * sprwidth * 2
                    write_all(f, data[start : start + sprwidth * 2])
        else:
            write_u16le(f, len(images))
            next_offset = 6 + 8 * len(images)
            for img in images:
                write_u32le(f, next_offset)
                write_u16le(f, img.width)
                write_u16le(f, img.height)
                next_offset += 2 * img.width * img.height

            for img in images:
                write_all(f, convert_image(img, rawmode).tobytes())


def write_c16_file(fname_or_stream, images, pixel_fmt="RGB565"):
    if pixel_fmt not in ("RGB555", "RGB565"):
        raise ValueError("pixel_fmt must be either 'RGB565' or 'RGB555'")

    with open_if_not_stream(fname_or_stream, "wb") as f:
        if pixel_fmt == "RGB555":
            rawmode = "BGR;15"
            write_u32le(f, 2)
        elif pixel_fmt == "RGB565":
            rawmode = "BGR;16"
            write_u32le(f, 3)

        write_u16le(f, len(images))

        output_position = 6
        for img in images:
            output_position += 4 + 4 * img.height

        # TODO: byteswap arrays if on big-endian?
        assert sys.byteorder == "little"

        compressed = io.BytesIO()
        for i, img in enumerate(images):
            img_width = img.width  # appears on profiling logs
            img_height = img.height  # appears on profiling logs
            data = array.array("H", convert_image(img, rawmode).tobytes())
            black8 = array.array("H", [0] * 8)

            def _match_black():
                nonlocal p
                nonlocal run_length
                nonlocal output_position
                # optimization: skip 8 black bytes at a time
                while p < img_width - 8:
                    start = img_width * j + p
                    if data[start : start + 8] == black8:
                        p += 8
                        run_length += 8
                    else:
                        break
                while p < img_width and data[img_width * j + p] == 0:
                    p += 1
                    run_length += 1
                output_position += 2
                write_u16le(compressed, run_length << 1)

            def _match_color():
                nonlocal p
                nonlocal run_length
                nonlocal output_position
                # optimization: use array.array.find to find next black pixel
                try:
                    run_length = data[img_width * j + p : img_width * (j + 1)].index(0)
                except ValueError:
                    run_length = img_width - p

                write_u16le(compressed, (run_length << 1) | 1)
                # optimization: use array.array's buffer interface to write directly,
                # rather than re-encoding as u16le.
                # WARNING: endianness needs to be correct before doing this
                write_all(
                    compressed, data[img_width * j + p : img_width * j + p + run_length]
                )
                p += run_length
                output_position += 2 + run_length * 2

            for j in range(img_height):
                write_u32le(f, output_position)
                if j == 0:
                    write_u16le(f, img_width)
                    write_u16le(f, img_height)

                p = 0
                while p < img_width:
                    run_length = 0
                    if data[img_width * j + p] == 0:
                        _match_black()
                    else:
                        _match_color()
                output_position += 2
                write_u16le(compressed, 0)
            output_position += 2
            write_u16le(compressed, 0)

        write_all(f, compressed.getbuffer())


def write_blk_file(fname_or_stream, image, pixel_fmt="RGB565"):
    if image.width % 128 != 0 or image.height % 128 != 0:
        raise ValueError(
            "Expected image size to be evenly divisible by 128x128, but got {}x{}".format(
                image.width, image.height
            )
        )

    if pixel_fmt not in ("RGB555", "RGB565"):
        raise ValueError("pixel_fmt must be either 'RGB565' or 'RGB555'")

    with open_if_not_stream(fname_or_stream, "wb") as f:
        width_blocks = image.width // 128
        height_blocks = image.height // 128

        if pixel_fmt == "RGB555":
            rawmode = "BGR;15"
            write_u32le(f, 0)
        elif pixel_fmt == "RGB565":
            rawmode = "BGR;16"
            write_u32le(f, 1)

        write_u16le(f, width_blocks)
        write_u16le(f, height_blocks)
        num_images = width_blocks * height_blocks
        write_u16le(f, num_images)

        for i in range(num_images):
            write_u32le(f, 10 + 8 * num_images + i * 128 * 128 * 2 - 4)  # offset
            write_u16le(f, 128)  # width
            write_u16le(f, 128)  # height

        data = convert_image(image, rawmode).tobytes()

        for i in range(num_images):
            y = i % height_blocks
            x = i // height_blocks
            for blocky in range(128):
                start = (y * 128 + blocky) * image.width * 2 + x * 128 * 2
                write_all(f, data[start : start + 128 * 2])


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


def cut_sheet_to_sprites(image, *, colorkey):
    all_runs = []
    previous_line_runs = []
    current_line_runs = []

    class Rect:
        __slots__ = ("left", "top", "width", "height")

        def __init__(self, left, top, width, height):
            self.left = left
            self.top = top
            self.width = width
            self.height = height

        def __repr__(self):
            return "<Rect left={} top={} width={} height={}>".format(
                self.left, self.top, self.width, self.height
            )

        @property
        def bottom(self):
            return self.top + self.height

        @property
        def right(self):
            return self.left + self.width

    image_width = image.width  # appears on profiling logs
    image_height = image.height  # appears on profiling logs

    data = image.tobytes()
    depth = len(colorkey)
    colorkey = bytes(colorkey)

    colorkey8 = bytes(colorkey) * 8

    def _getpixel(x, y):
        start = (y * image_width + x) * depth
        return data[start : start + depth]

    for y in range(image_height):
        x = 0
        while x < image_width:
            # skip past colorkey color
            # optimization: skip in batches of 8. this seems to be optimal for me,
            # speed increases up to batches of 16 where we hit a big slowdown.
            while x < image_width - 8:
                start = (y * image_width + x) * depth
                if data[start : start + 8 * depth] == colorkey8:
                    x += 8
                else:
                    break
            while x < image_width and _getpixel(x, y) == colorkey:
                x += 1

            # done with line?
            if x >= image_width:
                break

            # found an image, go as far right as we can
            start_x = x

            # optimization: if we have a matching run, then we can skip to the end
            for prev in previous_line_runs:
                if start_x >= prev.left and start_x < prev.right:
                    x = prev.right
                    break

            # go as far right as we can
            while x < image_width and _getpixel(x, y) != colorkey:
                x += 1
            end_x = x

            # update any previous run that we extended, or make a new run
            for prev in previous_line_runs:
                if (start_x >= prev.left and start_x < prev.right) or (
                    end_x >= prev.left and end_x < prev.right
                ):
                    new_left = min(start_x, prev.left)
                    new_right = max(end_x, prev.right)
                    prev.left = new_left
                    prev.width = new_right - new_left
                    prev.height += 1
                    current_line_runs.append(prev)
                    break
            else:
                new_rect = Rect(start_x, y, end_x - start_x, 1)
                all_runs.append(new_rect)
                current_line_runs.append(new_rect)

            x += 1

        previous_line_runs, current_line_runs = current_line_runs, []

    images = []
    for rect in all_runs:
        images.append(image.crop((rect.left, rect.top, rect.right, rect.bottom)))

    return images


def find_sprite_sheet_colorkey(image, *, width=5, height=5):
    top_left = [image.getpixel((x, y)) for x in range(5) for y in range(5)]
    if top_left[0] not in (0, (0, 0, 0), (0, 0, 0, 0)) and all(
        _ == top_left[0] for _ in top_left
    ):
        return top_left[0]
    return None
