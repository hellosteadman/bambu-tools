#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-cron',
	version = '0.1',
	description = 'A simple scheduling system that lets you define jobs that get performed at various intervals. Use a virtual "poor man\'s cron" or a single Django management command to run the jobs.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-cron',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.cron',
		'bambu.cron.migrations',
		'bambu.cron.management',
		'bambu.cron.management.commands'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)