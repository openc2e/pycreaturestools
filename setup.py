#!/usr/bin/env python

from distutils.core import setup

setup(
    name="pycreaturestools",
    version="0.1",
    description="",
    url="https://github.com/openc2e/pycreaturestools",
    install_requires=[
        "Pillow",
    ],
    extras_require={
        "dev": [
            "black",
        ],
        "test": [],
    },
)
