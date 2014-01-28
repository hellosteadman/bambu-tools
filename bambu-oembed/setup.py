#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-oembed',
	version = '0.1',
	description = 'Embed resources like YouTube videos, tweets and Flickr images by entering their URL on a single line of text. Methodology inspired by WordPress',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-oembed',
	install_requires = ['Django>=1.4'],
	namespace_packages = ['bambu'],
	packages = [
		'bambu.oembed',
		'bambu.oembed.migrations',
		'bambu.oembed.templatetags'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)