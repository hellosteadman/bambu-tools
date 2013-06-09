from django.template.response import TemplateResponse
from django.utils.importlib import import_module
from django.conf import settings
from bambu.mapping import PROVIDER

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