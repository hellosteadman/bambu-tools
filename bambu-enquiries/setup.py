#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-enquiries',
	version = '0.0.2',
	description = 'A simple model and contact form',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-enquiries',
	install_requires = [
		'Django>=1.4',
		'requests',
		'bambu-mail'
	],
	packages = [
		'bambu',
		'bambu.enquiries',
		'bambu.enquiries.migrations'
	],
	package_data = {
		'bambu.enquiries': [
			'templates/enquiries/*.html',
			'templates/enquiries/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)