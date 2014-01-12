#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-attachments',
	version = '0.0.2',
	description = 'A setup for handling generic model attachments',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-attachments',
	install_requires = ['Django>=1.4'],
	packages = [
		'bambu',
		'bambu.attachments',
		'bambu.attachments.migrations',
		'bambu.attachments.templatetags'
	],
	package_data = {
		'bambu.attachments': [
			'templates/attachments/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)