#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-international',
	version = '0.1',
	description = 'Provides a list of countries and a helper function to retrieve the Country object from a user\'s IP address',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-international',
	install_requires = [
		'Django>=1.4',
		'pygeoip'
	],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.international',
		'bambu.international.migrations'
	],
	package_data = {
		'bambu.international': [
			'fixtures/*.json',
			'fixtures/*.dat',
			'fixtures/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)