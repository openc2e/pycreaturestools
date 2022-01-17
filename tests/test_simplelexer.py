import unittest

from creaturestools._simplelexer import *


class TestSimpleLexer(unittest.TestCase):
    def test_simple_lexer(self):
        self.assertEqual(
            simplelexer('group AGNT "My Cool Agent"   \n"Key" "Value"\n"Key" 4\n'),
            [
                ("word", "group"),
                ("whitespace", " "),
                ("word", "AGNT"),
                ("whitespace", " "),
                ("string", "My Cool Agent"),
                ("whitespace", "   "),
                ("newline", "\n"),
                ("string", "Key"),
                ("whitespace", " "),
                ("string", "Value"),
                ("newline", "\n"),
                ("string", "Key"),
                ("whitespace", " "),
                ("integer", "4"),
                ("newline", "\n"),
                ("eoi", ""),
            ],
        )

        self.assertEqual(
            simplelexer('Pray-File "My Cool agent"'),
            [
                ("word", "Pray-File"),
                ("whitespace", " "),
                ("string", "My Cool agent"),
                ("eoi", ""),
            ],
        )

        self.assertEqual(
            simplelexer("attach snke.s16"),
            [
                ("word", "attach"),
                ("whitespace", " "),
                ("word", "snke.s16"),
                ("eoi", ""),
            ],
        )

        self.assertEqual(
            simplelexer('Agent Animation File = "snke.s16"'),
            [
                ("word", "Agent"),
                ("whitespace", " "),
                ("word", "Animation"),
                ("whitespace", " "),
                ("word", "File"),
                ("whitespace", " "),
                ("equals", "="),
                ("whitespace", " "),
                ("string", "snke.s16"),
                ("eoi", ""),
            ],
        )
        self.assertEqual(
            simplelexer("Agent Sprite First Image = 0"),
            [
                ("word", "Agent"),
                ("whitespace", " "),
                ("word", "Sprite"),
                ("whitespace", " "),
                ("word", "First"),
                ("whitespace", " "),
                ("word", "Image"),
                ("whitespace", " "),
                ("equals", "="),
                ("whitespace", " "),
                ("integer", "0"),
                ("eoi", ""),
            ],
        )
