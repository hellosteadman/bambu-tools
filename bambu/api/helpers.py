from django.views.decorators.csrf import csrf_exempt

try:
	from django.utils.functional import update_wrapper
except ImportError:
	from functools import update_wrapper

from django.utils.cache import patch_vary_headers
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.importlib import import_module
from oauth.oauth import build_authenticate_header
import sys

def trim_indent(docstring):
	"""
	Helps in formatting document strings for display within the project's developers' section.
	"""
	
	if not docstring:
		return ''
	
	lines = docstring.expandtabs().splitlines()
	indent = sys.maxint
	
	for line in lines[1:]:
		stripped = line.lstrip()
		if stripped:
			indent = min(indent, len(line) - len(stripped))
	
	trimmed = [lines[0].strip()]
	if indent < sys.maxint:
		for line in lines[1:]:
			trimmed.append(line[indent:].rstrip())
	
	while trimmed and not trimmed[-1]:
		trimmed.pop()
	
	while trimmed and not trimmed[0]:
		trimmed.pop(0)
	
	return '\n'.join(trimmed)

def form_initial_data(form_class, obj = None, **kwargs):
	"""
	Creates a dictionary of data to be passed as 'initial data' to a form.
	"""
	
	initial = {}
	for (name, field) in form_class.base_fields.items():
		initial[name] = field.prepare_value(getattr(obj, name, field.initial))
	
	for (key, value) in kwargs.items():
		if not '__' in key:
			initial[key] = value
	
	return initial

def wrap_api_function(site, view, detail_level, allowed_methods, processor):
	"""
	A decorator which wraps certain functions, so that a number of checks can be run before the function
	is called (ie: checking that the HTTP method is allowed).
	"""
	
	def wrapper(request, format, *args, **kwargs):
		if not request.method in allowed_methods:
			return HttpResponse('')
		
		response = site.api_view(
			view, request, format, *args,
			detail_level = detail_level + (request.method == 'POST' and 1 or 0),
			processor = processor,
			**kwargs
		)
		
		patch_vary_headers(response,
			getattr(settings, 'API_CACHE_VARY_HEADERS', ('Cookie',))
		)
		
		return response
	
	return csrf_exempt(
		update_wrapper(wrapper, view)
	)

def wrap_api_page(site, view, allowed_methods):
	"""
	A decorator which wraps certain functions, so that a number of checks can be run before the function
	is called (ie: checking that the HTTP method is allowed).
	"""
	
	def wrapper(request, *args, **kwargs):
		if not request.method in allowed_methods:
			return HttpResponse('')
		
		response = site.api_page(
			view, request, *args, **kwargs
		)
		
		patch_vary_headers(response,
			('X-Platform', 'X-Device', 'Cookie')
		)
		
		return response
	
	return update_wrapper(wrapper, view)

def generate_random_key(length = 32):
	"""
	Generates a random password for a user. This is purely for display purposes, from within the project's
	developers' section.
	"""
	
	return User.objects.make_random_password(length = length)

def send_oauth_error(err):
	"""
	Send an OAuth error to the HTTP client.
	"""
	
	response = HttpResponse(err.message.encode('utf-8'))
	response.status_code = 401
	
	realm = 'OAuth'
	header = build_authenticate_header(realm=realm)
	
	for k, v in header.iteritems():
		response[k] = v
	
	return response

def get_request_logger():
	logger = getattr(settings, 'API_REQUEST_LOGGER', 'bambu.api.requestlogging.DatabaseRequestLogger')
	module, dot, klass = logger.rpartition('.')
	
	module = import_module(module)
	klass = getattr(module, klass)
	
	return klass()