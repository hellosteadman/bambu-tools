#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-ffmpeg',
	version = '0.0.1',
	description = 'A shortcut function for converting video and audio files to HTML5-ready formats',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'http://pypi.python.org/pypi/bambu-ffmpeg',
	install_requires = [
		'Django>=1.4',
		'pymediainfo'
	],
	packages = [
		'bambu',
		'bambu.ffmpeg'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)