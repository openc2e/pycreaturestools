import io
import os
import random
import struct
import unittest

import creaturestools.sprites
from creaturestools._image_utils import convert_image

from PIL import Image


def generate_random_image(size):
    # paletted to save time generating random numbers
    img = Image.new("P", size)
    # If Python 3.9, use random.randbytes
    pixels = [random.getrandbits(8) for _ in range(size[0] * size[1])]
    img.putdata(pixels)
    img.putpalette(creaturestools.sprites.CREATURES1_PALETTE)
    return img


class TestSprites(unittest.TestCase):
    def _roundtrip(self, read_func, write_func, n=10, size=(100, 100)):
        random_images = [generate_random_image(size) for _ in range(n)]

        sprite1 = io.BytesIO()
        write_func(sprite1, random_images)
        sprite1.seek(0)
        images1 = read_func(sprite1)

        for (rand_img, img1) in zip(random_images, images1):
            self.assertEqual(rand_img.width, img1.width)
            self.assertEqual(rand_img.height, img1.height)
            if "rawmode" in img1.info:
                rand_img = convert_image(rand_img, img1.info["rawmode"])
            rand_img = convert_image(rand_img, "RGB")
            img1 = convert_image(img1, "RGB")
            self.assertEqual(rand_img.tobytes(), img1.tobytes())

        return (sprite1.getbuffer(), images1)

    def test_spr_roundtrip(self):
        self._roundtrip(
            creaturestools.sprites.read_spr_file, creaturestools.sprites.write_spr_file
        )

    # def test_spr_background(self):
    #     (sprite1, images1) = self._roundtrip(
    #         creaturestools.sprites.read_spr_file,
    #         creaturestools.sprites.write_spr_file,
    #         n=1,
    #         size=(8352, 1200),
    #     )
    #     num_sprites = struct.unpack("<H", sprite1[0:2])[0]
    #     self.assertEqual(num_sprites, 464)

    def test_s16_roundtrip(self):
        self._roundtrip(
            creaturestools.sprites.read_s16_file, creaturestools.sprites.write_s16_file
        )

    # def test_s16_background(self):
    #     (sprite1, images1) = self._roundtrip(
    #         creaturestools.sprites.read_s16_file,
    #         creaturestools.sprites.write_s16_file,
    #         n=1,
    #         size=(8352, 2400),
    #     )
    #     num_sprites = struct.unpack("<H", sprite1[4:6])[0]
    #     self.assertEqual(num_sprites, 928)

    def test_c16_roundtrip(self):
        self._roundtrip(
            creaturestools.sprites.read_c16_file, creaturestools.sprites.write_c16_file
        )

    def test_blk_roundtrip(self):
        self._roundtrip(
            lambda f: [creaturestools.sprites.read_blk_file(f)],
            lambda f, i: creaturestools.sprites.write_blk_file(f, i[0]),
            n=1,
            size=(640, 640),
        )
