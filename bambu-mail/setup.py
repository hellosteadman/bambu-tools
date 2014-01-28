#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-mail',
	version = '0.1',
	description = 'A shortcut function for sending template-based emails in HTML and plain-text format',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-mail',
	install_requires = [
		'Django>=1.4',
		'bambu-markup'
	],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.mail',
		'bambu.mail.newsletter'
	],
	package_data = {
		'bambu.mail': [
			'templates/mail/*.html',
			'templates/mail/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)