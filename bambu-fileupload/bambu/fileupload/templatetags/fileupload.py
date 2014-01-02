from django.template import Library
from django.conf import settings
from django.utils.importlib import import_module
import random, string

HANDLERS = dict(getattr(settings, 'FILEUPLOAD_HANDLERS', ()))
register = Library()

@register.inclusion_tag('fileupload/styles.inc.html')
def fileupload_styles():
	return {
		'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/')
	}

@register.inclusion_tag('fileupload/scripts.inc.html')
def fileupload_scripts():
	return {
		'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/')
	}

@register.inclusion_tag('fileupload/container.inc.html')
def fileupload_container(handler, parameters = '', callback_js = '(function(e) { window.location.href = document.location; })'):
	if not handler in HANDLERS:
		raise Exception('File uploaded handler %s not recognised' % handler)
	
	module, dot, func = HANDLERS[handler].rpartition('.')
	
	try:
		module = import_module(module)
	except ImportError, ex:
		raise Exception('Could not import module %s' % module, ex)
	
	try:
		func = getattr(module, func)
	except AttributeError, ex:
		raise Exception(
			'Could not load handler %s from module %s' % (func, module.__name__), ex
		)
	
	return {
		'id': random.choice(string.letters) + ''.join(random.sample(string.digits + string.letters, 6)),
		'handler': handler,
		'callback_js': callback_js,
		'params': parameters
	}

@register.filter
def fileuploadparam(value, name):
	return '%s=%s' % (name, value)