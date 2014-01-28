#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-sites',
	version = '0.1',
	description = 'Middleware that redirects users to a site\'s primary domain, based on the `django.contrib.sites` framework',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-sites',
	install_requires = ['Django>=1'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.sites'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)