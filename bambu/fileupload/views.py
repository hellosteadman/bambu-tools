from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.utils.importlib import import_module
from django.utils import simplejson
from urlparse import parse_qs
from mimetypes import guess_type
from logging import getLogger

HANDLERS = dict(getattr(settings, 'FILEUPLOAD_HANDLERS', ()))

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
		return HttpResponseBadRequest('No handler specified')
	
	if not handler in HANDLERS:
		logger.warn('File uploaded handler %s not recognised' % handler)
		return HttpResponseBadRequest('Handler %s not recognised' % handler)
	
	module, dot, func = HANDLERS[handler].rpartition('.')
	
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
		
		return HttpResponseBadRequest('Could not import module')
	
	try:
		func = getattr(module, func)
	except AttributeError, ex:
		logger.error(
			'Could not load handler %s from module %s' % (func, module.__name__),
			exc_info = True
		)
		
		return HttpResponseBadRequest('Could not load handler from module')
	
	if request.FILES == None:
		return HttpResponseBadRequest('No files appear to be attached')
	
	result = []
	success = 0
	fail = 0
	
	for f in request.FILES.getlist('fileupload[]'):
		f = UploadedFile(f)
		mimetype = None
		
		try:
			url = func(request, f, **params)
			# messages.success(request, '%s was uploaded successfully.' % f.name)
		except Exception, ex:
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
		elif isinstance(url, bool):
			success += 1
		else:
			logger.warn('File rejected by upload handler')
			fail += 1
			continue
	
	return HttpResponse(
		simplejson.dumps(result)
	)