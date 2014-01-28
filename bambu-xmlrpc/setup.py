#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-xmlrpc',
	version = '0.1',
	description = 'An extensible XML-RPC provider',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-xmlrpc',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.xmlrpc'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)