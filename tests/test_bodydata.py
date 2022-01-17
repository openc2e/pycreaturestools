import io
import unittest

from creaturestools.bodydata import *


class TestBodyData(unittest.TestCase):
    def test_bodydata(self):
        b = io.BytesIO(
            b""" 
            0 1 2 4
            5 6 5 4
        """
        )
        self.assertEqual(read_att_file(b), ([[(0, 1), (2, 4)], [(5, 6), (5, 4)]], ""))

        b = io.BytesIO(
            b"""
        
        28 16 17 31 
        21 14 25 33 
        15 19 33 25 
        17 28 29 14 

        left lower arm?
        upper arm?
        """
        )
        self.assertEqual(
            read_att_file(b),
            (
                [
                    [(28, 16), (17, 31)],
                    [(21, 14), (25, 33)],
                    [(15, 19), (33, 25)],
                    [(17, 28), (29, 14)],
                ],
                "left lower arm?\n        upper arm?",
            ),
        )
