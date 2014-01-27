#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-formatrules',
	version = '0.0.2',
	description = 'Syntactical sugar ontop of Markdown for adding extra formatting, expressed in a human-readable way.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-formatrules',
	install_requires = [
		'Django>=1.4',
		'markdown'
	],
	packages = [
		'bambu',
		'bambu.formatrules',
		'bambu.formatrules.formatters',
		'bambu.formatrules.templatetags'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)