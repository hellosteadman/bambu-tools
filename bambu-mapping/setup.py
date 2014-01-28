#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-mapping',
	version = '0.1',
	description = 'A pluggable, provider-based system for rendering maps',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-mapping',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.mapping',
		'bambu.mapping.providers',
		'bambu.mapping.templatetags'
	],
	package_data = {
		'bambu.mapping': [
			'static/mapping/leaflet/*.js',
			'static/mapping/leaflet/*.css',
			'static/mapping/leaflet/images/*.png',
			'templates/mapping/*.js'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)