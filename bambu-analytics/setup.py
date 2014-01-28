#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-analytics',
	version = '0.1',
	description = 'Provides a simple, pluggable system for analytics.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-analytics',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.analytics',
		'bambu.analytics.providers',
		'bambu.analytics.templatetags'
	],
	package_data = {
		'bambu.analytics': [
			'templates/analytics/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)