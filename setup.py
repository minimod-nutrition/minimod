# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages
from minimod.version import __version__

with open("reqs/base-requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

with open("README.md") as f:
    LONG_DESCRIPTION, LONG_DESC_TYPE = f.read(), "text/markdown"

NAME = "minimod"
AUTHOR_NAME, AUTHOR_EMAIL = "Aleksandr Michuda, Michael Jarvis and Steve Vosti", "amichuda@ucdavis.edu"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: GPLv3",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Intended Audience :: Social Scientists/Researchers"
    "Topic :: Scientific/Economics/Nutrition",
]
LICENSE = "GPLv3"
DESCRIPTION = "A Mixed Integer Solver for spatio-temporal nutrition interventions"
URL = "https://github.com/amichuda/minimod"
PYTHON_REQ = ">=3.5"

setup(
    name=NAME,
    version=__version__,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    python_requires=PYTHON_REQ,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    packages=find_packages(),
)
