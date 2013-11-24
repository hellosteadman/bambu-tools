#!/usr/bin/env python
from distutils.core import setup

setup(
	name = 'bambu-tools',
	version = '3.3',
	description = 'Tools for Django webapps',
	author = 'Mark Steadman',
	author_email = 'mark@flamingtarball.com',
	url = 'http://pypi.python.org/pypi/bambu-tools',
	install_requires = [
		'Django>=1.4',
		'Markdown>=2.2.1',
		'django-taggit>=0.9.3',
		'oauth>=1.0.1',
		'oauth2>=1.5.211',
		'pyquery>=1.2.4',
		'python-dateutil>=1.5',
		'markdown',
		'requests>=1.1.0',
		'sorl-thumbnail>=11.12',
		'twitter>=1.9.1'
	],
	packages = [
		'bambu',
		'bambu.analytics', 'bambu.analytics.providers', 'bambu.analytics.templatetags',
		'bambu.api', 'bambu.api.auth', 'bambu.api.migrations', 'bambu.api.templatetags', 'bambu.api.xml',
		'bambu.attachments', 'bambu.attachments.migrations', 'bambu.attachments.templatetags',
		'bambu.blog', 'bambu.blog.management', 'bambu.blog.management.commands', 'bambu.blog.migrations', 'bambu.blog.templatetags', 
		'bambu.bootstrap', 'bambu.bootstrap.templatetags',
		'bambu.codemirror',
		'bambu.comments', 'bambu.comments.templatetags', 'bambu.comments.migrations',
		'bambu.cron', 'bambu.cron.migrations', 'bambu.cron.management', 'bambu.cron.management.commands',
		'bambu.dataportability', 'bambu.dataportability.management', 'bambu.dataportability.management.commands', 'bambu.dataportability.migrations',
		'bambu.enqueue', 'bambu.enqueue.templatetags',
		'bambu.enquiries', 'bambu.enquiries.migrations',
		'bambu.faq', 'bambu.faq.migrations',
		'bambu.ffmpeg',
		'bambu.fileupload', 'bambu.fileupload.templatetags',
		'bambu.formatrules', 'bambu.formatrules.formatters', 'bambu.formatrules.templatetags',
		'bambu.grids',
		'bambu.international', 'bambu.international.migrations',
		'bambu.jwplayer', 'bambu.jwplayer.templatetags',
		'bambu.mail', 'bambu.mail.newsletter',
		'bambu.mapping', 'bambu.mapping.providers', 'bambu.mapping.templatetags',
		'bambu.markup', 'bambu.markup.templatetags',
		'bambu.minidetect',
		'bambu.navigation', 'bambu.navigation.management', 'bambu.navigation.management.commands', 'bambu.navigation.templatetags',
		'bambu.notifications', 'bambu.notifications.migrations', 'bambu.notifications.templatetags',
		'bambu.pages', 'bambu.pages.migrations',
		'bambu.payments', 'bambu.payments.gateways', 'bambu.payments.migrations',
		'bambu.preview', 'bambu.preview.migrations',
		'bambu.pusher', 'bambu.pusher.templatetags',
		'bambu.oembed', 'bambu.oembed.migrations', 'bambu.oembed.templatetags',
		'bambu.opengraph', 'bambu.opengraph.templatetags',
		'bambu.saas', 'bambu.saas.migrations', 'bambu.saas.views',
		'bambu.signup', 'bambu.signup.migrations', 'bambu.signup.views',
		'bambu.sites',
		'bambu.urlshortener', 'bambu.urlshortener.migrations', 'bambu.urlshortener.providers',
		'bambu.webhooks', 'bambu.webhooks.migrations',
		'bambu.xmlrpc'
	],
	package_data = {
		'': ['requirements.txt'],
		'bambu.analytics': [
			'templates/analytics/*.html'
		],
		'bambu.api': [
			'static/api/js/google-prettify/*.js',
			'static/api/js/google-prettify/*.css',
			'templates/api/*.html',
			'templates/api/apps/*.html',
			'templates/api/auth/*.html',
			'templates/api/auth/oauth/*.html',
			'templates/api/doc/*.html'
		],
		'bambu.attachments': [
			'templates/attachments/*.html'
		],
		'bambu.blog': [
			'templates/admin/blog/post/*.html',
			'templates/blog/*.html',
			'templates/search/indexes/blog/*.txt',
			'templates/preview/blog/*.html',
			'static/blog/*.js'
		],
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
		],
		'bambu.codemirror': [
			'static/codemirror/keymap/*.js',
			'static/codemirror/lib/*.css',
			'static/codemirror/lib/*.js',
			'static/codemirror/lib/util/*.css',
			'static/codemirror/lib/util/*.js',
			'static/codemirror/mode/clike/*.js',
			'static/codemirror/mode/clike/*.html',
			'static/codemirror/mode/clojure/*.js',
			'static/codemirror/mode/clojure/*.html',
			'static/codemirror/mode/coffeescript/*.js',
			'static/codemirror/mode/coffeescript/*.html',
			'static/codemirror/mode/coffeescript/LICENSE',
			'static/codemirror/mode/css/*.js',
			'static/codemirror/mode/css/*.html',
			'static/codemirror/mode/diff/*.js',
			'static/codemirror/mode/diff/*.html',
			'static/codemirror/mode/ecl/*.js',
			'static/codemirror/mode/ecl/*.html',
			'static/codemirror/mode/erlang/*.js',
			'static/codemirror/mode/erlang/*.html',
			'static/codemirror/mode/gfm/*.js',
			'static/codemirror/mode/gfm/*.html',
			'static/codemirror/mode/go/*.js',
			'static/codemirror/mode/go/*.html',
			'static/codemirror/mode/groovy/*.js',
			'static/codemirror/mode/groovy/*.html',
			'static/codemirror/mode/haskell/*.js',
			'static/codemirror/mode/haskell/*.html',
			'static/codemirror/mode/htmlembedded/*.js',
			'static/codemirror/mode/htmlembedded/*.html',
			'static/codemirror/mode/htmlmixed/*.js',
			'static/codemirror/mode/htmlmixed/*.html',
			'static/codemirror/mode/javascript/*.js',
			'static/codemirror/mode/javascript/*.html',
			'static/codemirror/mode/jinja2/*.js',
			'static/codemirror/mode/jinja2/*.html',
			'static/codemirror/mode/less/*.js',
			'static/codemirror/mode/less/*.html',
			'static/codemirror/mode/lua/*.js',
			'static/codemirror/mode/lua/*.html',
			'static/codemirror/mode/markdown/*.js',
			'static/codemirror/mode/markdown/*.html',
			'static/codemirror/mode/mysql/*.js',
			'static/codemirror/mode/mysql/*.html',
			'static/codemirror/mode/ntriples/*.js',
			'static/codemirror/mode/ntriples/*.html',
			'static/codemirror/mode/pascal/*.js',
			'static/codemirror/mode/pascal/*.html',
			'static/codemirror/mode/pascal/LICENSE',
			'static/codemirror/mode/perl/*.js',
			'static/codemirror/mode/perl/*.html',
			'static/codemirror/mode/perl/LICENSE',
			'static/codemirror/mode/php/*.js',
			'static/codemirror/mode/php/*.html',
			'static/codemirror/mode/pig/*.js',
			'static/codemirror/mode/pig/*.html',
			'static/codemirror/mode/plsql/*.js',
			'static/codemirror/mode/plsql/*.html',
			'static/codemirror/mode/properties/*.js',
			'static/codemirror/mode/properties/*.html',
			'static/codemirror/mode/python/*.js',
			'static/codemirror/mode/python/*.html',
			'static/codemirror/mode/python/*.txt',
			'static/codemirror/mode/r/*.js',
			'static/codemirror/mode/r/*.html',
			'static/codemirror/mode/r/LICENSE',
			'static/codemirror/mode/rpm/changes/*.js',
			'static/codemirror/mode/rpm/changes/*.html',
			'static/codemirror/mode/rpm/spec/*.js',
			'static/codemirror/mode/rpm/spec/*.css',
			'static/codemirror/mode/rpm/spec/*.html',
			'static/codemirror/mode/rst/*.js',
			'static/codemirror/mode/rst/*.html',
			'static/codemirror/mode/ruby/*.js',
			'static/codemirror/mode/ruby/*.html',
			'static/codemirror/mode/ruby/LICENSE',
			'static/codemirror/mode/rust/*.js',
			'static/codemirror/mode/rust/*.html',
			'static/codemirror/mode/scheme/*.js',
			'static/codemirror/mode/scheme/*.html',
			'static/codemirror/mode/shell/*.js',
			'static/codemirror/mode/shell/*.html',
			'static/codemirror/mode/smalltalk/*.js',
			'static/codemirror/mode/smalltalk/*.html',
			'static/codemirror/mode/smarty/*.js',
			'static/codemirror/mode/smarty/*.html',
			'static/codemirror/mode/sparql/*.js',
			'static/codemirror/mode/sparql/*.html',
			'static/codemirror/mode/stex/*.js',
			'static/codemirror/mode/stex/*.html',
			'static/codemirror/mode/tiddlywiki/*.js',
			'static/codemirror/mode/tiddlywiki/*.css',
			'static/codemirror/mode/tiddlywiki/*.html',
			'static/codemirror/mode/tiki/*.css',
			'static/codemirror/mode/tiki/*.js',
			'static/codemirror/mode/tiki/*.html',
			'static/codemirror/mode/vbscript/*.js',
			'static/codemirror/mode/vbscript/*.html',
			'static/codemirror/mode/velocity/*.js',
			'static/codemirror/mode/velocity/*.html',
			'static/codemirror/mode/verilog/*.js',
			'static/codemirror/mode/verilog/*.html',
			'static/codemirror/mode/xml/*.js',
			'static/codemirror/mode/xml/*.html',
			'static/codemirror/mode/xquery/*.js',
			'static/codemirror/mode/xquery/*.html',
			'static/codemirror/mode/xquery/LICENSE',
			'static/codemirror/mode/xquery/test/*.html',
			'static/codemirror/mode/xquery/test/*.js',
			'static/codemirror/mode/yaml/*.js',
			'static/codemirror/mode/yaml/*.html'
			'static/codemirror/theme/*.css'
		],
		'bambu.comments': [
			'templates/comments/*.html',
			'templates/comments/*.txt',
			'templates/search/indexes/comments/*.txt'
		],
		'bambu.dataportability': [
			'templates/dataportability/*.html',
			'templates/dataportability/mail/*.txt',
			'templates/dataportability/notifications/*.txt'
		],
		'bambu.enquiries': [
			'templates/enquiries/*.html',
			'templates/enquiries/*.txt'
		],
		'bambu.faq': [
			'templates/faq/*.html',
			'fixtures/initial_data.json'
		],
		'bambu.fileupload': [
			'static/fileupload/css/*.css',
			'static/fileupload/img/*.gif',
			'static/fileupload/js/*.js',
			'static/fileupload/js/cors/*.js',
			'static/fileupload/js/vendor/*.js',
			'templates/fileupload/*.html'
		],
		'bambu.grids': [
			'static/grids/js/*.js'
		],
		'bambu.international': [
			'fixtures/*.json',
			'fixtures/*.dat',
			'fixtures/*.txt'
		],
		'bambu.jwplayer': [
			'static/jwplayer/*.js',
			'static/jwplayer/*.txt',
			'static/jwplayer/*.swf',
			'static/jwplayer/*.png',
			'static/jwplayer/skins/*.zip',
			'templates/jwplayer/*.html'
		],
		'bambu.mapping': [
			'static/mapping/leaflet/*.js',
			'static/mapping/leaflet/*.css',
			'static/mapping/leaflet/images/*.png',
			'templates/mapping/*.js'
		],
		'bambu.mail': [
			'templates/mail/*.html',
			'templates/mail/*.txt'
		],
		'bambu.minidetect': [
			'fixtures/*.txt'
		],
		'bambu.notifications': [
			'static/notifications/css/*.css',
			'templates/notifications/*.html',
			'templates/notifications/mail/*.html',
			'templates/notifications/mail/*.txt'
		],
		'bambu.pages': [
			'templates/pages/*.html',
			'templates/preview/pages/*.html',
			'templates/search/indexes/pages/*.txt'
		],
		'bambu.payments': [
			'fixtures/*.json',
			'templates/payments/*.html',
			'templates/payments/*.txt',
			'templates/payments/gateways/*.html',
			'templates/payments/gateways/paymill/*.html',
			'static/payments/*.png',
			'static/payments/gateways/*.png'
		],
		'bambu.preview': [
			'static/preview/img/*.gif',
			'static/preview/css/*.css',
			'static/preview/js/*.js',
			'templates/admin/preview/*.html',
			'templates/preview/*.html'
		],
		'bambu.pusher': [
			'templates/pusher/*.html'
		],
		'bambu.opengraph': [
			'templates/opengraph/*.html'
		],
		'bambu.saas': [
			'templates/saas/*.html',
			'templates/saas/mail/*.txt',
			'templates/saas/profile/*.html',
			'templates/registration/*.html',
			'templates/saas/notifications/*.txt',
			'templates/saas/mail/*.txt',
			'static/saas/css/*.css',
			'static/saas/img/*.png'
		],
		'bambu.signup': [
			'templates/signup/*.html',
			'templates/signup/mail/*.txt'
		],
		'bambu.webhooks': [
			'templates/webhooks/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)