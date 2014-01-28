#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-urlshortener',
	version = '0.1',
	description = 'Shrink a URL using an internal or external shortening service',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-urlshortener',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.urlshortener',
		'bambu.urlshortener.migrations',
		'bambu.urlshortener.providers'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)