#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-comments',
	version = '0.1',
	description = 'Generic model commenting',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-comments',
	install_requires = [
		'Django>=1.4',
		'pyquery',
		'html2text',
		'markdown',
		'bambu-mail'
	],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.comments',
		'bambu.comments.templatetags',
		'bambu.comments.migrations'
	],
	package_data = {
		'bambu.comments': [
			'templates/comments/*.html',
			'templates/comments/*.txt',
			'templates/search/indexes/comments/*.txt'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)