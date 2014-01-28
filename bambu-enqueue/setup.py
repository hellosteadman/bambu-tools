#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-enqueue',
	version = '0.1',
	description = 'Enqueue CSS and JavaScript (inspired by WordPress)',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-enqueue',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.enqueue',
		'bambu.enqueue.templatetags'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)