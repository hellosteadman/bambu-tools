#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-jwplayer',
	version = '0.1',
	description = 'A wrapper around the JWPlayer',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-jwplayer',
	install_requires = ['Django>=1.4'],
	packages = [
		'bambu',
		'bambu.jwplayer',
		'bambu.jwplayer.templatetags'
	],
	package_data = {
		'bambu.jwplayer': [
			'static/jwplayer/*.js',
			'static/jwplayer/*.txt',
			'static/jwplayer/*.swf',
			'static/jwplayer/*.png',
			'static/jwplayer/skins/*.zip',
			'templates/jwplayer/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)