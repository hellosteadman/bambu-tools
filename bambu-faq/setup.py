#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-faq',
	version = '0.1',
	description = 'A simple set of models for a Frequently-Asked-Questions site',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-faq',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.faq',
		'bambu.faq.migrations'
	],
	package_data = {
		'bambu.faq': [
			'templates/faq/*.html',
			'fixtures/initial_data.json'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)