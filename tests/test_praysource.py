import io
import pathlib
import unittest

from creaturestools.praysource import *


class TestPraySource(unittest.TestCase):
    def test_parse_pray_source(self):
        source = """
        
        "en-GB"
        
        group DSAG "My Agent"
        "Int tag 1" 42
        "Int tag 2" 47
        "String tag 1" "hello"
        "String tag 2" "world"
        "External string tag" @ "myscript.cos"
        
        inline FILE "mysprite.c16" "mysprite.png"
        inline FILE "mysound.wav" "mysound.flac"
        
        """

        parsed = parse_pray_source_file(io.BytesIO(source.encode()))
        self.assertEqual(
            parsed,
            [
                (
                    "DSAG",
                    "My Agent",
                    {
                        "Int tag 1": 42,
                        "Int tag 2": 47,
                        "String tag 1": "hello",
                        "String tag 2": "world",
                        "External string tag": pathlib.Path("myscript.cos"),
                    },
                ),
                ("FILE", "mysprite.c16", pathlib.Path("mysprite.png")),
                ("FILE", "mysound.wav", pathlib.Path("mysound.flac")),
            ],
        )
