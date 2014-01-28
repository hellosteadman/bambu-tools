#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'bambu',
    version = '0.1',
    description = 'Namespace package for the Bambu Tools toolset',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'http://pypi.python.org/pypi/bambu-analytics',
    packages = ['bambu'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)