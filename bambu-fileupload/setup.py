#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-fileupload',
	version = '0.1',
	description = 'A wrapper around the jQuery.fileupload library',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-fileupload',
	install_requires = ['Django>=1.4'],
	packages = [
		'bambu',
		'bambu.fileupload',
		'bambu.fileupload.templatetags'
	],
	package_data = {
		'bambu.fileupload': [
			'static/fileupload/css/*.css',
			'static/fileupload/img/*.gif',
			'static/fileupload/js/*.js',
			'static/fileupload/js/cors/*.js',
			'static/fileupload/js/vendor/*.js',
			'templates/fileupload/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)