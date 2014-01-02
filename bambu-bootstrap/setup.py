#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-bootstrap',
	version = '0.0.1',
	description = 'Use Twitter\'s Bootstrap CSS framework to build your app. All the views Bambu uses all extend a base template which you create, that can be based on a skeleton Bootstrap template. Shortcut tags let you easily add breadcrumb trails and icons to your apps.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-bootstrap',
	install_requires = ['Django>=1.4'],
	packages = [
		'bambu',
		'bambu.bootstrap',
		'bambu.bootstrap.templatetags'
	],
	package_data = {
		'bambu.bootstrap': [
			'static/bootstrap/css/*.css',
			'static/bootstrap/css/jquery-ui/*.css',
			'static/bootstrap/css/jquery-ui/images/*.png',
			'static/bootstrap/js/*.js',
			'static/bootstrap/img/*.png',
			'static/bootstrap/font/*.*',
			'static/bootstrap/3.0/css/*.css',
			'static/bootstrap/3.0/js/*.js',
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