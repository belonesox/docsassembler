#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Setup for the package
"""

from setuptools import setup

requirements = [ 
    'gladtex',
    'lxml',
    'pandoc-include',
    'scons==4.4.0'
]

setup(
    name='docsassembler',
    install_requires=requirements,
    version_config=True,
    setup_requires=['setuptools_git_versioning'],
    packages=['docsassembler'],
    entry_points={
        'console_scripts': [
            'docsassembler=docsassembler.cli:main',
            'das=docsassembler.cli:main',
            'das-dasws=docsassembler.cli:dasws',
        ],
    },
    author_email = "stanislav.fomin@gmail.com",
)

