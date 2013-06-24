from django.conf import settings
from django.utils.importlib import import_module

URL_LENGTH = getattr(settings, 'SHORTURL_LENGTH', 7)

def shorten(url):
	from threading import local
	_thread_locals = local()
	
	provider = getattr(_thread_locals, 'bambu_urlshortener', None)
	if not provider:
		module, dot, klass = getattr(settings, 'SHORTURL_PROVIDER',
			'bambu.urlshortener.providers.db.DatabaseProvider'
		).rpartition('.')
		
		module = import_module(module)
		_thread_locals.bambu_urlshortener = getattr(module, klass)
	
	return _thread_locals.bambu_urlshortener().shorten(url)