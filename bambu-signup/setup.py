#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-signup',
	version = '0.0.2',
	description = 'A fluid signup method for free web apps',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-signup',
	install_requires = [
		'Django>=1.4',
		'bambu-mail'
	],
	packages = [
		'bambu',
		'bambu.signup',
		'bambu.signup.migrations',
		'bambu.signup.views'
	],
	package_data = {
		'bambu.signup': [
			'templates/signup/*.html',
			'templates/signup/mail/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)