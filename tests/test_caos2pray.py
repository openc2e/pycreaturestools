import io
import pathlib
import unittest

from creaturestools.caos2pray import *


class TestCaos2PraySource(unittest.TestCase):
    def test_parse_caos2pray_source(self):

        s = """
**CAOS2PRAY
*# Pray-File "Snakey.agents"
*# C3-Name "Snakey C3"
*# DS-Name "Snakey DS"
*# attach snke.s16
*# desc = "A polite critter"
*# Agent Animation File = "snke.s16"
*# Agent Animation String = "0"
*# Agent Sprite First Image = 0
*# Agent Animation Gallery = "snke"
*# Web URL = "creatures.wiki"
*# Web Label = "Creatures Wiki"

inst
new: simp 2 15 1000 "snke" 16 0 3500

* etc...

rscr
    outs "hi there"
        
        """

        self.maxDiff = None
        self.assertEqual(
            parse_caos2pray_source_file(io.BytesIO(s.encode())),
            [
                (
                    "AGNT",
                    "Snakey C3",
                    {
                        "Agent Animation File": "snke.s16",
                        "Agent Animation Gallery": "snke",
                        "Agent Animation String": "0",
                        "Agent Description": "A polite critter",
                        "Agent Sprite First Image": 0,
                        "Agent Type": 0,
                        "Dependency 1": "snke.s16",
                        "Dependency Category 1": 2,
                        "Dependency Count": 1,
                        "Remove script": 'rscr\n    outs "hi there"\n',
                        "Script 1": "\n"
                        "**CAOS2PRAY\n"
                        '*# Pray-File "Snakey.agents"\n'
                        '*# C3-Name "Snakey C3"\n'
                        '*# DS-Name "Snakey DS"\n'
                        "*# attach snke.s16\n"
                        '*# desc = "A polite critter"\n'
                        '*# Agent Animation File = "snke.s16"\n'
                        '*# Agent Animation String = "0"\n'
                        "*# Agent Sprite First Image = 0\n"
                        '*# Agent Animation Gallery = "snke"\n'
                        '*# Web URL = "creatures.wiki"\n'
                        '*# Web Label = "Creatures Wiki"\n'
                        "\n"
                        "inst\n"
                        'new: simp 2 15 1000 "snke" 16 0 3500\n'
                        "\n"
                        "* etc...\n"
                        "\n"
                        "rscr\n"
                        '    outs "hi there"\n'
                        "        \n"
                        "        ",
                        "Script Count": 1,
                        "Web Label": "Creatures Wiki",
                        "Web URL": "creatures.wiki",
                    },
                ),
                (
                    "DSAG",
                    "Snakey DS",
                    {
                        "Agent Animation File": "snke.s16",
                        "Agent Animation Gallery": "snke",
                        "Agent Animation String": "0",
                        "Agent Description": "A polite critter",
                        "Agent Sprite First Image": 0,
                        "Agent Type": 0,
                        "Dependency 1": "snke.s16",
                        "Dependency Category 1": 2,
                        "Dependency Count": 1,
                        "Remove script": 'rscr\n    outs "hi there"\n',
                        "Script 1": "\n"
                        "**CAOS2PRAY\n"
                        '*# Pray-File "Snakey.agents"\n'
                        '*# C3-Name "Snakey C3"\n'
                        '*# DS-Name "Snakey DS"\n'
                        "*# attach snke.s16\n"
                        '*# desc = "A polite critter"\n'
                        '*# Agent Animation File = "snke.s16"\n'
                        '*# Agent Animation String = "0"\n'
                        "*# Agent Sprite First Image = 0\n"
                        '*# Agent Animation Gallery = "snke"\n'
                        '*# Web URL = "creatures.wiki"\n'
                        '*# Web Label = "Creatures Wiki"\n'
                        "\n"
                        "inst\n"
                        'new: simp 2 15 1000 "snke" 16 0 3500\n'
                        "\n"
                        "* etc...\n"
                        "\n"
                        "rscr\n"
                        '    outs "hi there"\n'
                        "        \n"
                        "        ",
                        "Script Count": 1,
                        "Web Label": "Creatures Wiki",
                        "Web URL": "creatures.wiki",
                    },
                ),
                ("FILE", "snke.s16", pathlib.Path("snke.s16")),
            ],
        )
