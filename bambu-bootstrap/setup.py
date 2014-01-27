#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-bootstrap',
	version = '0.0.3',
	description = 'Use Twitter\'s Bootstrap CSS framework to build your app. All the views Bambu uses all extend a base template which you create, that can be based on a skeleton Bootstrap template. Shortcut tags let you easily add breadcrumb trails and icons to your apps.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-bootstrap',
	install_requires = ['Django>=1.4'],
	packages = [
		'bambu',
		'bambu.bootstrap',
		'bambu.bootstrap.templatetags',
		'bambu.bootstrap.v2',
		'bambu.bootstrap.v2.templatetags',
		'bambu.bootstrap.v3',
		'bambu.bootstrap.v3.templatetags'
	],
	package_data = {
		'bambu.bootstrap.v2': [
			'static/bootstrap/css/*.css',
			'static/bootstrap/css/jquery-ui/*.css',
			'static/bootstrap/css/jquery-ui/images/*.png',
			'static/bootstrap/js/*.js',
			'static/bootstrap/img/*.png',
			'static/bootstrap/font/*.*',
			'templates/bootstrap/*.html',
			'templates/search/*.html',
			'templates/*.html'
		],
		'bambu.bootstrap.v3': [
			'static/bootstrap/css/*.css',
			'static/bootstrap/js/*.js',
			'static/bootstrap/fonts/*.*',
			'templates/bootstrap/*.html',
			'templates/search/*.html',
			'templates/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)