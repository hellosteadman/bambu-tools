#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-navigation',
	version = '0.1',
	description = 'A set of template tags and settings for creating automatically-built menus',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-navigation',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.navigation',
		'bambu.navigation.management',
		'bambu.navigation.management.commands',
		'bambu.navigation.templatetags'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)