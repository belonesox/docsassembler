#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Setup for the package
"""

from setuptools import setup

setup(
    name='docsassembler',
    version_config=True,
    setup_requires=['setuptools-git-versioning'],
    packages=['docsassembler'],
    entry_points={
        'console_scripts': [
            'docsassembler=docsassembler.cli:main',
	        'das=docsassembler.cli:main'
        ],
    },
    author_email = "stanislav.fomin@gmail.com",
)

