#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-dataportability',
	version = '0.0.2',
	description = 'Generic import and export tools',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-dataportability',
	install_requires = [
		'Django>=1.4',
		'bambu-mail'
	],
	packages = [
		'bambu',
		'bambu.dataportability',
		'bambu.dataportability.management',
		'bambu.dataportability.management.commands',
		'bambu.dataportability.migrations'
	],
	package_data = {
		'bambu.dataportability': [
			'templates/dataportability/*.html',
			'templates/dataportability/mail/*.txt',
			'templates/dataportability/notifications/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)