from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.utils.importlib import import_module
from urlparse import parse_qs
from mimetypes import guess_type
from logging import getLogger
from bambu.fileupload import DEFAULT_HANDLERS

try:
	import json as simplejson
except ImportError:
	from django.utils import simplejson

HANDLERS = dict(getattr(settings, 'FILEUPLOAD_HANDLERS', DEFAULT_HANDLERS))

@login_required
@csrf_exempt
def upload(request):
	handler = request.GET.get('handler')
	logger = getLogger('bambu.fileupload')
	params = request.GET.get('params')

	if params:
		try:
			params = parse_qs(params)
		except:
			return HttpResponseBadRequest('Badly formatted parameters')
	else:
		params = {}

	if not handler:
		logger.warn('File uploaded via AJAX with no handler')
		return HttpResponseBadRequest('No handler specified', content_type = 'application/json')

	if not handler in HANDLERS:
		logger.warn('File uploaded handler %s not recognised' % handler)
		return HttpResponseBadRequest('Handler %s not recognised' % handler, content_type = 'application/json')

	h = HANDLERS[handler]
	if isinstance(h, (list, tuple)):
		h = list(h)
		func = h.pop(0)
	else:
		func = h

	module, dot, func = func.rpartition('.')

	try:
		module = import_module(module)
	except ImportError, ex:
		logger.error('Could not import module', exc_info = True,
			extra = {
				'data': {
					'module': module
				}
			}
		)

		return HttpResponseBadRequest('Could not import module', content_type = 'application/json')

	try:
		func = getattr(module, func)
	except AttributeError, ex:
		logger.error(
			'Could not load handler %s from module %s' % (func, module.__name__),
			exc_info = True
		)

		return HttpResponseBadRequest('Could not load handler from module', content_type = 'application/json')

	if request.FILES == None:
		return HttpResponseBadRequest('No files appear to be attached', content_type = 'application/json')

	result = []
	success = 0
	fail = 0

	for f in request.FILES.getlist('fileupload[]'):
		f = UploadedFile(f)
		mimetype = None

		try:
			url = func(request, f, **params)
		except Exception, ex:
			if settings.DEBUG:
				raise

			messages.error(request, '%s was not uploaded.' % f.name)
			logger.error('Error uploading file via %s handler' % handler, exc_info = True)
			continue

		if url and isinstance(url, (str, unicode)):
			success += 1
			mimetype, encoding = guess_type(url)
			result.append(
				{
					'name': f.name,
					'size': f.file.size,
					'url': url,
					'type': mimetype,
					'encoding': encoding
				}
			)
		elif isinstance(url, bool) and url:
			success += 1
		else:
			logger.warn('File rejected by upload handler')
			fail += 1
			continue

	return HttpResponse(
		simplejson.dumps(result),
		content_type = 'application/json'
	)

@login_required
@csrf_exempt
def delete(request):
	handler = request.GET.get('handler')
	logger = getLogger('bambu.fileupload')
	params = request.GET.get('params')

	if params:
		try:
			params = parse_qs(params)
		except:
			return HttpResponseBadRequest('Badly formatted parameters', content_type = 'application/json')
	else:
		params = {}

	if not handler:
		logger.warn('File uploaded via AJAX with no handler')
		return HttpResponseBadRequest('No handler specified', content_type = 'application/json')

	if not handler in HANDLERS:
		logger.warn('File uploaded handler %s not recognised' % handler)
		return HttpResponseBadRequest('Handler %s not recognised' % handler, content_type = 'application/json')

	h = HANDLERS[handler]
	if isinstance(h, (list, tuple)):
		h = list(h)
		func = h.pop(2)
	else:
		return HttpResponseBadRequest('Handler %s does not have a delete function' % handler, content_type = 'application/json')

	module, dot, func = func.rpartition('.')

	try:
		module = import_module(module)
	except ImportError, ex:
		logger.error('Could not import module', exc_info = True,
			extra = {
				'data': {
					'module': module
				}
			}
		)

		return HttpResponseBadRequest('Could not import module', content_type = 'application/json')

	try:
		func = getattr(module, func)
	except AttributeError, ex:
		logger.error(
			'Could not load handler %s from module %s' % (func, module.__name__),
			exc_info = True
		)

		return HttpResponseBadRequest('Could not load handler from module', content_type = 'application/json')

	f = request.GET.get('f')
	result = func(request, f, **params)
	return HttpResponse(
		simplejson.dumps(result),
		content_type = 'application/json'
	)

@login_required
def filelist(request):
	handler = request.GET.get('handler')
	logger = getLogger('bambu.fileupload')
	params = request.GET.get('params')

	if params:
		try:
			params = parse_qs(params)
		except:
			return HttpResponseBadRequest('Badly formatted parameters', content_type = 'application/json')
	else:
		params = {}

	if not handler:
		logger.warn('File uploaded via AJAX with no handler')
		return HttpResponseBadRequest('No handler specified', content_type = 'application/json')

	if not handler in HANDLERS:
		logger.warn('File uploaded handler %s not recognised' % handler)
		return HttpResponseBadRequest('Handler %s not recognised' % handler, content_type = 'application/json')

	h = HANDLERS[handler]
	if isinstance(h, (list, tuple)):
		h = list(h)
		func = h.pop(3)
	else:
		return HttpResponseBadRequest('Handler %s does not have a delete function' % handler, content_type = 'application/json')

	module, dot, func = func.rpartition('.')

	try:
		module = import_module(module)
	except ImportError, ex:
		logger.error('Could not import module', exc_info = True,
			extra = {
				'data': {
					'module': module
				}
			}
		)

		return HttpResponseBadRequest('Could not import module', content_type = 'application/json')

	try:
		func = getattr(module, func)
	except AttributeError, ex:
		logger.error(
			'Could not load handler %s from module %s' % (func, module.__name__),
			exc_info = True
		)

		return HttpResponseBadRequest('Could not load handler from module', content_type = 'application/json')

	f = request.GET.get('f')
	result = func(request, f, **params)
	return HttpResponse(
		simplejson.dumps(result),
		content_type = 'application/json'
	)
