#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-payments',
	version = '0.0.2',
	description = 'Pluggable, provider-based payment handling',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-payments',
	install_requires = [
		'Django>=1.4',
		'bambu-mail'
	],
	packages = [
		'bambu',
		'bambu.payments',
		'bambu.payments.gateways',
		'bambu.payments.migrations'
	],
	package_data = {
		'bambu.payments': [
			'fixtures/*.json',
			'templates/payments/*.html',
			'templates/payments/*.txt',
			'templates/payments/gateways/*.html',
			'templates/payments/gateways/paymill/*.html',
			'static/payments/*.png',
			'static/payments/gateways/*.png'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)