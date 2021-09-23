# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from setuptools import setup, find_packages

PKG_NAME = "ddr"


def get_version():
    with open('ddr.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=PKG_NAME,
    version=get_version(),
    author="jonisb",
    author_email="github.com@JsBComputing.se",
    description="A ddrescue TUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonisb/ddr",
    #packages=[PKG_NAME],
    packages=find_packages(),
    python_requires='>=3.6, <4',
)
