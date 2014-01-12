#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-grids',
	version = '0.0.2',
	description = 'Show tabular data with filtering options and support for AJAX and pushstate',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-grids',
	install_requires = ['Django>=1.4'],
	packages = [
		'bambu',
		'bambu.grids'
	],
	package_data = {
		'bambu.grids': [
			'static/grids/js/*.js'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)