#!/usr/bin/env python

from distutils.core import setup

setup(
    name="pycreaturestools",
    version="0.1",
    description="",
    url="https://github.com/openc2e/pycreaturestools",
    packages=["creaturestools"],
    install_requires=[
        "Pillow",
    ],
    extras_require={
        "dev": [
            "black",
            "isort>=5",
        ],
        "test": [],
    },
)
