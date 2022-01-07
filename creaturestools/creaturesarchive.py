import zlib

from ._io_utils import *


def decompress_creaturesarchive_compressed_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        data = f.read()
        magic = b"Creatures Evolution Engine - Archived information file. zLib 1.13 compressed.\x1a\x04"
        if not data.startswith(magic):
            raise ReadError(
                "Expected file to start with {}, but got {}".format(
                    magic, data[0 : len(magic)]
                )
            )
        return zlib.decompress(data[len(magic) :])
