from PIL import Image
import array
import struct
import io

from ._io_utils import *
from .exceptions import *


def read_s16_file(f):
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
    offsets = []
    widths = []
    heights = []
    next_offset = 6 + (8 * num_images)
    for _ in range(num_images):
        offsets.append(read_u32le(f))
        if offsets[-1] != next_offset:
            raise ReadError(
                "Expected image offset to be {}, but got {}".format(
                    next_offset, offsets[i]
                )
            )
        widths.append(read_u16le(f))
        heights.append(read_u16le(f))
        next_offset += 2 * widths[-1] * heights[-1]

    images = []
    for i in range(num_images):
        image = Image.frombytes(
            "RGB",
            (widths[i], heights[i]),
            read_exact(f, 2 * widths[i] * heights[i]),
            "raw",
            rawmode,
        )
        images.append(image)

    return images


def read_c16_file(f):
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
                        (j * widths[i] + p) * 2 : (j * widths[i] + p + run_length) * 2
                    ] = read_exact(f, run_length * 2)
                else:
                    # bytearray() initializes memory to zero, so we don't need to do anything
                    pass
                p += run_length

            end_of_line = read_u16le(f)
            if end_of_line != 0:
                raise ReadError(
                    "Expected end-of-line byte to be 0, but got {}".format(end_of_line)
                )
        end_of_image = read_u16le(f)
        if end_of_image != 0:
            raise ReadError(
                "Expected end-of-image byte to be 0, but got {}".format(end_of_image)
            )
        image = Image.frombytes(
            "RGB", (widths[i], heights[i]), bytes(data), "raw", rawmode
        )
        images.append(image)


def read_blk_file(f):
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
                width_blocks, height_blocks, width_blocks * height_blocks, num_images
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
                "Expected image size to be 128x128, but got {}x{}".format(width, height)
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

    return Image.frombytes(
        "RGB",
        (totalwidth, totalheight),
        bytes(data),
        "raw",
        rawmode,
    )


def write_s16_file(f, images, pixel_fmt="RGB565"):
    if pixel_fmt == "RGB555":
        rawmode = "BGR;15"
        write_u32le(f, 0)
    elif pixel_fmt == "RGB565":
        rawmode = "BGR;16"
        write_u32le(f, 1)
    else:
        raise ValueError("pixel_fmt must be either 'RGB565' or 'RGB555'")

    write_u16le(f, len(images))
    next_offset = 6 + 8 * len(images)
    for img in images:
        write_u32le(f, next_offset)
        write_u16le(f, img.width)
        write_u16le(f, img.height)
        next_offset += 2 * img.width * img.height

    for img in images:
        write_all(f, img.convert(rawmode).tobytes())


def write_c16_file(f, images, pixel_fmt="RGB565"):
    if pixel_fmt == "RGB555":
        rawmode = "BGR;15"
        write_u32le(f, 2)
    elif pixel_fmt == "RGB565":
        rawmode = "BGR;16"
        write_u32le(f, 3)
    else:
        raise ValueError("pixel_fmt must be either 'RGB565' or 'RGB555'")

    write_u16le(f, len(images))

    output_position = 6
    for img in images:
        output_position += 4 + 4 * img.height

    compressed_data = []
    for i, img in enumerate(images):
        data = array.array("H", img.convert(rawmode).tobytes())
        compressed = io.BytesIO()

        for j in range(img.height):
            write_u32le(f, output_position)
            if j == 0:
                write_u16le(f, img.width)
                write_u16le(f, img.height)

            p = 0
            while p < img.width:
                run_length = 0
                if data[img.width * j + p] == 0:
                    while p < img.width and data[img.width * j + p] == 0:
                        p += 1
                        run_length += 1
                    output_position += 2
                    write_u16le(compressed, run_length << 1)
                else:
                    while p < img.width and data[img.width * j + p] != 0:
                        p += 1
                        run_length += 1
                    output_position += 2 + run_length * 2
                    write_u16le(compressed, (run_length << 1) | 1)
                    write_many_u16le(
                        compressed,
                        data[img.width * j + (p - run_length) : img.width * j + p],
                    )
            output_position += 2
            write_u16le(compressed, 0)
        output_position += 2
        write_u16le(compressed, 0)
        compressed_data.append(compressed.getbuffer())

    for compressed in compressed_data:
        write_all(f, compressed)


def write_blk_file(f, image, pixel_fmt="RGB565"):
    if image.width % 128 != 0 or image.height % 128 != 0:
        raise ValueError(
            "Expected image size to be evenly divisible by 128x128, but got {}x{}".format(
                image.width, image.height
            )
        )

    width_blocks = image.width // 128
    height_blocks = image.height // 128

    if pixel_fmt == "RGB555":
        rawmode = "BGR;15"
        write_u32le(f, 0)
    elif pixel_fmt == "RGB565":
        rawmode = "BGR;16"
        write_u32le(f, 1)
    else:
        raise ValueError("pixel_fmt must be either 'RGB565' or 'RGB555'")

    write_u16le(f, width_blocks)
    write_u16le(f, height_blocks)
    num_images = width_blocks * height_blocks
    write_u16le(f, num_images)

    next_offset = 10 + 8 * num_images
    for _ in range(num_images):
        write_u32le(f, next_offset - 4)
        write_u16le(f, 128)  # width
        write_u16le(f, 128)  # height

    data = image.convert(rawmode).tobytes()

    for i in range(num_images):
        y = i % height_blocks
        x = i // height_blocks
        for blocky in range(128):
            start = (y * 128 + blocky) * image.width * 2 + x * 128 * 2
            write_all(f, data[start : start + 128 * 2])
