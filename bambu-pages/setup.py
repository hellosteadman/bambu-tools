#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-pages',
	version = '0.0.2',
	description = 'Tools for Django webapps',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-pages',
	install_requires = [
		'Django>=1.4',
		'bambu-attachments',
		'bambu-markup',
		'bambu-formatrules'
	],
	packages = [
		'bambu',
		'bambu.pages',
		'bambu.pages.migrations'
	],
	package_data = {
		'bambu.pages': [
			'templates/pages/*.html',
			'templates/search/indexes/pages/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)