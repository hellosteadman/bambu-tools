#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-saas',
	version = '0.0.3',
	description = 'A set of models, templates, views and helpers to manage the plans-and-pricing side of a paid-for web app',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-saas',
	install_requires = [
		'Django>=1.4',
		'bambu-payments',
		'bambu-mail'
	],
	packages = [
		'bambu',
		'bambu.saas',
		'bambu.saas.migrations',
		'bambu.saas.views'
	],
	package_data = {
		'bambu.saas': [
			'templates/saas/*.html',
			'templates/saas/mail/*.txt',
			'templates/saas/profile/*.html',
			'templates/registration/*.html',
			'templates/saas/notifications/*.txt',
			'templates/saas/mail/*.txt',
			'static/saas/css/*.css',
			'static/saas/img/*.png'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)