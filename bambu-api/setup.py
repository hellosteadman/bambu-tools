#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
	name = 'bambu-api',
	version = '0.5.2',
	description = 'Quickly expose your models to a JSON or XML API, authenticated via HTTP or OAuth.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-analytics',
	long_description = open(path.join(path.dirname(__file__), 'README')).read(),
	install_requires = [
		'Django>=1.4',
		'oauth',
		'oauth2'
	],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.api',
		'bambu.api.auth',
		'bambu.api.migrations',
		'bambu.api.templatetags',
		'bambu.api.xml'
	],
	package_data = {
		'bambu.api': [
			'templates/api/*.html',
			'templates/api/apps/*.html',
			'templates/api/auth/*.html',
			'templates/api/auth/oauth/*.html',
			'templates/api/doc/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)
