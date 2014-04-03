from django.template import Library
from django.conf import settings
from django.utils.importlib import import_module
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from bambu.fileupload import DEFAULT_HANDLERS
from uuid import uuid4
import random, string

HANDLERS = dict(
	getattr(settings, 'FILEUPLOAD_HANDLERS', DEFAULT_HANDLERS)
)

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

@register.inclusion_tag('fileupload/container.inc.html', takes_context = True)
def fileupload_container(context, handler = 'attachments', parameters = '', callback_js = None):
	if not handler in HANDLERS:
		raise Exception('File uploaded handler %s not recognised' % handler)

	h = HANDLERS[handler]
	deletable = False
	listable = False

	if isinstance(h, (list, tuple)):
		h = list(h)
		func = h.pop(0)
		deletable = len(h) > 1
		listable = len(h) > 2

		if any(h) and not callback_js:
			callback_js = h.pop(0)
	else:
		func = h

	if not callback_js:
		callback_js = '(function(e) { window.location.href = document.location; })'

	module, dot, func = func.rpartition('.')

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

	if 'request' in context:
		request = context['request']
		if request.method == 'POST' and '_bambu_fileupload_guid' in request.POST:
			guid = request.POST['_bambu_fileupload_guid']
		else:
			guid = unicode(uuid4())
	else:
		guid = None

	if not parameters:
		parameters = 'guid=%s' % guid

	container_id = 'bambu_fileupload_%s' % ''.join(random.sample(string.digits + string.letters, 6))
	script = """<script>jQuery(document).ready(
		function($) {
			bambu.fileupload.init('%s','%s?%s', %s%s);
			%s
		}
	);</script>""" % (
		container_id,
		reverse('fileupload'),
		urlencode(
			{
				'handler': handler,
				'params': parameters
			}
		),
		callback_js,
		deletable and ", '%s?%s'" % (
			reverse('fileupload_delete'),
			urlencode(
				{
					'handler': handler,
					'params': parameters
				}
			)
		) or '',
		listable and (
			'bambu.fileupload.list(\'%s\', \'%s?%s\');' % (container_id,
				reverse('fileupload_list'),
				urlencode(
					{
						'handler': handler,
						'params': parameters
					}
				)
			)
		) or ''
	)

	if guid:
		script = u'<input name="_bambu_fileupload_guid" value="%s" type="hidden" />%s' % (guid, script)

	return {
		'id': container_id,
		'guid': guid,
		'script': script
	}

@register.filter
def fileuploadparam(value, name):
	return '%s=%s' % (name, value)
