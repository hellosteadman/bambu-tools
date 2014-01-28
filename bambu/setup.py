#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'bambu',
    version = '0.1',
    description = 'Base module for bambu-tools',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'http://pypi.python.org/pypi/bambu-analytics',
    install_requires = [
        'bambu',
        'Django>=1.4',
        'oauth',
        'oauth2'
    ],
    packages = ['bambu'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)