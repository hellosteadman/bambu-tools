#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-buffer',
	version = '0.1',
	description = 'Post to Buffer and manage profile settings through a Django-powered site',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-buffer',
	namespace_packages = ['bambu'],
	packages = [
		'bambu.buffer',
        'bambu.buffer.migrations'
	],
    package_data = {
        'bambu.buffer': [
            'templates/buffer/*.html'
        ]
    },
    install_requires = [
		'Django>=1.6',
		'requests>=2.0'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)
