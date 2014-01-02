from django.template.response import TemplateResponse
from django.utils.importlib import import_module
from django.utils.http import urlencode
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from bambu.mapping import PROVIDER
from urllib import urlopen

def functions_js(request):
	module, comma, klass = PROVIDER.rpartition('.')
	module = import_module(module)
	klass = getattr(module, klass)
	kwargs = getattr(settings, 'MAPPING_SETTINGS')
	map_id = request.GET.get('m')
	provider = klass(map_id, **kwargs)
	
	return TemplateResponse(
		request,
		'mapping/bambu.mapping.js',
		{
			'provider': provider
		},
		mimetype = 'text/javascript'
	)

def funnel_json(request):
	url = request.GET.get('url')
	json_callback = request.GET.get('json_callback')
	callback = request.GET.get('callback')
	kw = {}
	
	referrer = request.META.get('HTTP_REFERER')
	if not referrer:
		return HttpResponseBadRequest()
	
	slash = referrer.find('//')
	referrer = referrer[slash + 2:referrer.find('/', slash + 3)]
	if not referrer:
		return HttpResponseBadRequest()
	
	try:
		Site.objects.get(domain__iexact = referrer)
	except Site.DoesNotExist:
		return HttpResponseBadRequest()
	
	if json_callback or callback:
		q = url.find('?')
		if q > -1:
			url += '&'
		else:
			url += '?'
	
	if json_callback:
		kw['json_callback'] = json_callback
	elif callback:
		kw['callback'] = callback
	
	if any(kw):
		url += urlencode(kw)
	
	return HttpResponse(
		urlopen(url).read(),
		mimetype = 'application/json'
	)