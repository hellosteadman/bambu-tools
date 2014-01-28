#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-api',
	version = '0.1.3',
	description = 'Quickly expose your models to a JSON or XML API, authenticated via HTTP or OAuth.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-analytics',
	install_requires = [
		'Django>=1.4',
		'oauth',
		'oauth2'
	],
	packages = [
		'bambu.api',
		'bambu.api.auth',
		'bambu.api.migrations',
		'bambu.api.templatetags',
		'bambu.api.xml'
	],
	package_data = {
		'bambu.api': [
			'static/api/js/google-prettify/*.js',
			'static/api/js/google-prettify/*.css',
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