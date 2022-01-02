from PIL import Image, ImageOps

from ._io_utils import *
from .exceptions import *
from .sprites import CREATURES1_PALETTE


def _decode_c1_string(b):
    num_ascii = 0
    for c in b:
        if c < 128:
            num_ascii += 1
    try:
        if num_ascii * 2 > len(b) and False:
            # if more than half ascii, likely CP1252
            return b.decode("cp1252")
        else:
            # if not more than half ascii, try cp932
            # TODO: better heuristics? creatures strings in Japanese have a lot of
            # double-byte katakana characters which should be recognizable.
            return b.decode("cp932")
    except:
        # Welp.
        return b.decode("ascii", "backslashreplace")


class Cob1File:
    __slots__ = [
        "name",
        "description",
        "quantity_available",
        "quantity_used",
        "sprinkle",
        "expiration_date",
        "object_scripts",
        "install_scripts",
        "sprite",
    ]

    def __init__(self):
        for _ in self.__slots__:
            setattr(self, _, None)

    def __repr__(self):
        return (
            "<Cob1File "
            + " ".join("{}={!r}".format(_, getattr(self, _)) for _ in self.__slots__)
            + ">"
        )


def read_cob1_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        version = read_u16le(f)
        if version != 1:
            raise ReadError("Expected COB version to be 1, but got {}".format(version))

        cob1 = Cob1File()

        cob1.quantity_available = read_u16le(f)
        expiration_month = read_u32le(f)
        expiration_day = read_u32le(f)
        expiration_year = read_u32le(f)
        cob1.expiration_date = (expiration_year, expiration_month, expiration_day)

        num_object_scripts = read_u16le(f)
        num_install_scripts = read_u16le(f)
        cob1.quantity_used = read_u16le(f)

        cob1.sprinkle = read_u16le(f)
        if cob1.sprinkle not in (0, 1):
            raise ReadError(
                "Expected sprinkle to be 0 or 1, but got {}".format(cob1.sprinkle)
            )
        cob1.sprinkle = bool(cob1.sprinkle)

        cob1.object_scripts = []
        for _ in range(num_object_scripts):
            cob1.object_scripts.append(_read_cstring(f).decode("ascii"))
        cob1.install_scripts = []
        for _ in range(num_install_scripts):
            cob1.install_scripts.append(_read_cstring(f).decode("ascii"))
        # TODO: check for japanese?

        sprite_storage_width = read_u32le(f)
        sprite_height = read_u32le(f)
        sprite_width = read_u16le(f)
        if sprite_width != sprite_storage_width:
            raise NotImplementedError(
                "Expected sprite_width {} to be same as sprite_storage_width {}".format(
                    sprite_width, sprite_storage_width
                )
            )

        if sprite_storage_width * sprite_height > 0:
            sprite = Image.frombytes(
                "P",
                (sprite_storage_width, sprite_height),
                read_exact(f, sprite_storage_width * sprite_height),
            )
            sprite.putpalette(CREATURES1_PALETTE)
            cob1.sprite = ImageOps.flip(sprite)

        cob1.name = _decode_c1_string(_read_cstring(f))
        cob1.description = _decode_c1_string(_read_cstring(f))
        # TODO: check for japanese?

        return cob1
