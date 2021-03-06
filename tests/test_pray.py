import io
import pathlib
import unittest

from creaturestools.pray import *

PRAY_RAW = b"PRAYDSAGMy Agent\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00g\x00\x00\x00\x8f\x00\x00\x00\x01\x00\x00\x00x\xdacb``\xe0\x04b\xcf\xbc\x12\x85\x92\xc4t\x05C-4\x01#} \x87\x19\x88\x85\x81\xd8\xb5\xa2$\xb5(/1G\xa1\xb8\xa4(3/\x1d\xa4@\x02(\x9c_ZR\xac\xa0T\x92\x91Y\xac\x00D\x89\n\xc5\xc9E\x99\x05%J\\<@\xb9`\xb8J\x05CV ?#5''\x1fM\xc2\x08$Q\x9e_\x94\x93\x02\x00\xb9\xbd\"mFILEhello.txt\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00x\xda\xcbH\xcd\xc9\xc9W(\xcf/\xcaI\xe1\x02\x00\x1er\x04g"

PRAY_PARSED = [
    (
        "DSAG",
        "My Agent",
        {
            "External string tag": 'outs "this is a script"\n',
            "Int tag 1": 42,
            "Int tag 2": 47,
            "String tag 1": "hello",
            "String tag 2": "world",
        },
    ),
    ("FILE", "hello.txt", b"hello world\n"),
]


class TestPray(unittest.TestCase):
    def test_read_pray_file(self):
        pray = read_pray_file(io.BytesIO(PRAY_RAW))
        self.assertEqual(pray, PRAY_PARSED)

    def test_write_pray_file(self):
        f = io.BytesIO()
        write_pray_file(f, PRAY_PARSED, compression=9)
        self.assertEqual(bytes(f.getbuffer()), PRAY_RAW)
