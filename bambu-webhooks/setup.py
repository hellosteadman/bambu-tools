#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-webhooks',
	version = '0.0.2',
	description = 'Create webhooks and allow users to assign URLs to them',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-webhooks',
	install_requires = [
		'Django>=1.4',
		'requests'
	],
	packages = [
		'bambu',
		'bambu.webhooks',
		'bambu.webhooks.migrations'
	],
	package_data = {
		'bambu.webhooks': [
			'templates/webhooks/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)