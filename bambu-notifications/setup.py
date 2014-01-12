#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-notifications',
	version = '0.0.2',
	description = 'Generic, developer-defined model notifications that can be delivered via a set of pluggable, provider-based endpoints (email, SMS, Pusher, etc)',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-notifications',
	install_requires = [
		'Django>=1.4',
		'markdown'
	],
	packages = [
		'bambu',
		'bambu.notifications',
		'bambu.notifications.migrations',
		'bambu.notifications.templatetags'
	],
	package_data = {
		'bambu.notifications': [
			'static/notifications/css/*.css',
			'templates/notifications/*.html',
			'templates/notifications/mail/*.html',
			'templates/notifications/mail/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)