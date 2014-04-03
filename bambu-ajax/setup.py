#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-ajax',
	version = '0.1',
	description = 'AJAX utility functions for Django',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-ajax',
	namespace_packages = ['bambu'],
	packages = [
		'bambu.ajax'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)
