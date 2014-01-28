#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-pusher',
	version = '0.1',
	description = 'A wrapper around the Pusher API',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-pusher',
	install_requires = [
		'Django>=1.4',
		'requests'
	],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.pusher',
		'bambu.pusher.templatetags'
	],
	package_data = {
		'bambu.pusher': [
			'templates/pusher/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)