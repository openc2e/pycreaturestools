import io

from PIL import Image, ImageOps

from ._io_utils import *
from .caos import format_c1_caos
from .exceptions import *
from .sprites import CREATURES1_PALETTE, write_spr_file


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
            cob1.object_scripts.append(read_cstring(f).decode("ascii"))
        cob1.install_scripts = []
        for _ in range(num_install_scripts):
            cob1.install_scripts.append(read_cstring(f).decode("ascii"))
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

        cob1.name = _decode_c1_string(read_cstring(f))
        cob1.description = _decode_c1_string(read_cstring(f))
        # TODO: check for japanese?

        return cob1


def generate_caos2cob1_source(cob, rcb, filenamefunc=lambda name, data: name):
    s = ""
    s += "** CAOS2Cob\n"
    s += '*# C1-Name "{}"\n'.format(cob.name)
    # s += "*# Cob File = \"{}\"\n".format(filename_root + ".cob")
    s += "*# Quantity Available = {}\n".format(cob.quantity_available)
    if cob.quantity_used:
        s += "*# Quantity Used = {}\n".format(cob.quantity_used)
    if cob.sprinkle:
        s += "*# Sprinkle = {}\n".format(str(cob.sprinkle).lower())
    if cob.expiration_date != (0, 0, 0):
        s += "*# Expiry Date = {}-{}-{}\n".format(*cob.expiration_date)

    b = io.BytesIO()
    write_spr_file(b, [cob.sprite])
    sprite_filename = filenamefunc(cob.name + ".spr", b.getbuffer())
    s += '*# Thumbnail = "{}"\n'.format(sprite_filename)

    s += '*# Description = "{}"\n'.format(cob.description)
    s += "\n"
    for install_script in cob.install_scripts:
        s += format_c1_caos("iscr," + install_script + ",endm")
        s += "\n"
    for object_script in cob.object_scripts:
        s += format_c1_caos(object_script + ",endm")
        s += "\n"
    if rcb:
        for install_script in rcb.install_scripts:
            s += format_c1_caos("rscr," + install_script)
            s += "\n"

    return s


import io

import PIL.Image

from ._io_utils import *
from .sprites import *


class Cob2AgntBlock:
    __slots__ = [
        "quantity_remaining",
        "last_used_datetime",
        "reuse_interval_seconds",
        "expiration_date",
        "name",
        "description",
        "install_script",
        "remove_script",
        "event_scripts",
        "dependencies",
        "thumbnail",
    ]

    def __init__(self):
        for _ in self.__slots__:
            setattr(self, _, None)

    def __repr__(self):
        return (
            "<Cob2AgntBlock "
            + " ".join("{}={!r}".format(_, getattr(self, _)) for _ in self.__slots__)
            + ">"
        )


class Cob2FileBlock:
    __slots__ = [
        "filename",
        "filetype",
        "data",
    ]

    def __init__(self):
        for _ in self.__slots__:
            setattr(self, _, None)

    def __repr__(self):
        return (
            "<Cob2FileBlock "
            + " ".join("{}={!r}".format(_, getattr(self, _)) for _ in self.__slots__)
            + ">"
        )


class Cob2AuthBlock:
    __slots__ = [
        "created_date",
        "version",
        "revision",
        "author_name",
        "author_email",
        "url",
        "comments",
    ]

    def __init__(self):
        for _ in self.__slots__:
            setattr(self, _, None)

    def __repr__(self):
        return (
            "<Cob2AuthBlock "
            + " ".join("{}={!r}".format(_, getattr(self, _)) for _ in self.__slots__)
            + ">"
        )


def _decode_c2_string(b):
    return b.decode("cp1252")


def _read_null_terminated_c2_string(f):
    return _decode_c2_string(read_null_terminated_string(f))


def is_cob2_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        return peek_exact(f, 4) == b"cob2"


def read_cob2_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        magic = read_exact(f, 4)
        if magic != b"cob2":
            raise Exception("Expected magic to be b'cob2', but got {}".format(magic))

        blocks = []

        while f.peek():
            block_type = read_exact(f, 4)
            block_size = read_u32le(f)
            if block_type == b"agnt":
                agnt_block = Cob2AgntBlock()
                agnt_block.quantity_remaining = read_u16le(f)
                agnt_block.last_used_datetime = read_u32le(
                    f
                )  # TODO: parse as datetime?
                agnt_block.reuse_interval_seconds = read_u32le(f)
                expiration_day = read_u8(f)
                expiration_month = read_u8(f)
                expiration_year = read_u16le(f)
                agnt_block.expiration_date = (
                    expiration_year,
                    expiration_month,
                    expiration_day,
                )  # TODO: parse as datetime?
                padding = read_exact(f, 12)
                if padding != b"\x00" * 12:
                    raise Exception(
                        "Expected padding to be zero, but got {}".format(padding)
                    )
                agnt_block.name = _read_null_terminated_c2_string(f)
                agnt_block.description = _read_null_terminated_c2_string(f)
                agnt_block.install_script = _read_null_terminated_c2_string(f)
                agnt_block.remove_script = _read_null_terminated_c2_string(f)
                num_event_scripts = read_u16le(f)
                agnt_block.event_scripts = []
                for _ in range(num_event_scripts):
                    agnt_block.event_scripts.append(_read_null_terminated_c2_string(f))
                num_dependencies = read_u16le(f)
                agnt_block.dependencies = []
                for _ in range(num_dependencies):
                    dep_type = read_u16le(f)
                    dep_name = _read_null_terminated_c2_string(f)
                    agnt_block.dependencies.append((dep_type, dep_name))
                thumbnail_width = read_u16le(f)
                thumbnail_height = read_u16le(f)
                thumbnail_data = read_exact(f, thumbnail_width * thumbnail_height * 2)
                agnt_block.thumbnail = PIL.Image.frombytes(
                    "RGB",
                    (thumbnail_width, thumbnail_height),
                    thumbnail_data,
                    "raw",
                    "BGR;16",
                )
                blocks.append(agnt_block)

            elif block_type == b"file":
                file_block = Cob2FileBlock()
                file_block.filetype = read_u16le(f)
                padding = read_exact(f, 4)
                if padding != b"\x00\x00\x00\x00":
                    raise Exception(
                        "Expected padding to be zero, but got {}".format(padding)
                    )
                file_size = read_u32le(f)
                file_block.filename = read_null_terminated_string(f).decode(
                    "ascii"
                )  # TODO: cp1252?
                header_length = len(file_block.filename) + 1 + 10
                if file_size + header_length != block_size:
                    raise Exception(
                        "Expected file size {} plus header {} to match block size {}".format(
                            file_size, header_length, block_size
                        )
                    )
                file_block.data = read_exact(f, file_size)
                blocks.append(file_block)

            elif block_type == b"auth":
                auth_block = Cob2AuthBlock()
                p = f.tell()
                auth_created_day = read_u8(f)
                auth_created_month = read_u8(f)
                auth_created_year = read_u16le(f)
                auth_block.created_date = (
                    auth_created_year,
                    auth_created_month,
                    auth_created_day,
                )  # TODO: parse as datetime?
                auth_block.version = read_u8(f)
                auth_block.revision = read_u8(f)
                auth_block.author_name = _read_null_terminated_c2_string(f)
                auth_block.author_email = _read_null_terminated_c2_string(f)
                auth_block.url = _read_null_terminated_c2_string(f)
                auth_block.comments = _read_null_terminated_c2_string(f)
                if f.tell() - p != block_size:
                    raise Exception(
                        "Expected auth data size {} to match block size {}".format(
                            f.tell() - p, block_size
                        )
                    )
                blocks.append(auth_block)

            else:
                raise NotImplementedError(
                    "Expected b'agnt', b'file', or b'auth', but got {}".format(
                        block_type
                    )
                )
    return blocks


def generate_cob2_source(blocks, filenamefunc=lambda name, data: name):
    s = ""
    for block in blocks:
        if isinstance(block, Cob2AgntBlock):
            if s.count("\n") > 1 and s.split("\n")[-2].startswith("inline file"):
                s += "\n"

            s += 'group agnt "{}"\n'.format(block.name)
            #  s += "\"Name\" \"{}\"\n".format(block.name)
            s += '"Description" "{}"\n'.format(block.description)
            s += '"Quantity Remaining" {}\n'.format(block.quantity_remaining)
            s += '"Last Used Datetime" {}\n'.format(block.last_used_datetime)
            s += '"Reuse Interval" {}\n'.format(block.reuse_interval_seconds)
            s += '"Expiration Day" {}\n'.format(block.expiration_date[0])
            s += '"Expiration Month" {}\n'.format(block.expiration_date[1])
            s += '"Expiration Year" {}\n'.format(block.expiration_date[2])
            s += '"Install Script" "{}"\n'.format(block.install_script)
            s += '"Remove Script" "{}"\n'.format(block.remove_script)
            s += '"Event Script Count" {}\n'.format(len(block.event_scripts))
            for i, script in enumerate(block.event_scripts):
                s += '"Event Script {}" "{}"\n'.format(i + 1, script)
            s += '"Dependency Count" {}\n'.format(len(block.dependencies))
            for i, (type, name) in enumerate(block.dependencies):
                s += '"Dependency {}" "{}"\n'.format(i + 1, name)
                s += '"Dependency Category {}" {}\n'.format(i + 1, type)
            b = io.BytesIO()
            write_s16_file(b, [block.thumbnail])
            thumbnail_path = filenamefunc(block.name + ".s16", b.getbuffer())
            s += '"Thumbnail" @ "{}"\n'.format(thumbnail_path)
            # full_script = format_c2_caos("iscr," + block.install_script + ",endm") + "\n" + ''.join(format_c2_caos(script + ",endm") + "\n" for script in block.event_scripts) + format_c2_caos("rscr," + block.remove_script + ",endm")
            # print(full_script)
            s += "\n"

        elif isinstance(block, Cob2FileBlock):
            # TODO: assert filename and filetype are appropriate
            if block.filename.lower().split(".")[-1] == "s16":
                expected_filetype = 0
            elif block.filename.lower().split(".")[-1] == "wav":
                expected_filetype = 1
            else:
                raise NotImplementedError('Filetype "{}"'.format(block.filename))
            if expected_filetype != block.filetype:
                raise NotImplementedError(
                    "Expected file type {} for file {!r}, but got {}".format(
                        expected_filetype, block.filename, block.filetype
                    )
                )
            file_path = filenamefunc(block.filename, block.data)
            s += 'inline file "{}" "{}"\n'.format(block.filename, file_path)

        elif isinstance(block, Cob2AuthBlock):
            if s.count("\n") > 1 and s.split("\n")[-2].startswith("inline file"):
                s += "\n"

            s += 'group auth "{}"\n'.format(block.author_name)
            s += '"Created Day" {}\n'.format(block.created_date[0])
            s += '"Created Month" {}\n'.format(block.created_date[1])
            s += '"Created Year" {}\n'.format(block.created_date[2])
            s += '"Version" {}\n'.format(block.version)
            s += '"Revision" {}\n'.format(block.revision)
            # s += "\"Author Name\" \"{}\"\n".format(block.author_name)
            s += '"Author Email" "{}"\n'.format(block.author_email)
            s += '"URL" "{}"\n'.format(block.url)
            s += '"Comments" "{}"\n'.format(block.comments)
            s += "\n"

        else:
            raise NotImplementedError(block)
    return s.strip() + "\n"
