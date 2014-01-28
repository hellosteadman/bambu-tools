#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-minidetect',
	version = '0.1',
	description = 'Tools for Django webapps',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-minidetect',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.minidetect'
	],
	package_data = {
		'bambu.minidetect': [
			'fixtures/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)