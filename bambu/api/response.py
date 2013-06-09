from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ImproperlyConfigured
from bambu.api import serialisers

SERIALISERS = {
	'json': serialisers.JSONSerialiser,
	'xml': serialisers.XMLSerialiser
}

MIME_TYPES = {
	'json': 'application/json',
	'xml': 'application/xml'
}

def get_serialiser(format, request, processor, max_detail_level):
	if format in SERIALISERS:
		return SERIALISERS[format](request, processor, max_detail_level)
	
	raise ImproperlyConfigured('Unrecognised API serialiser "%s"' % format)

class APIResponse(HttpResponse):
	detail_level = 2
	
	def __init__(self, format, request, data, **kwargs):
		if 'detail_level' in kwargs:
			self.detail_level = kwargs['detail_level']
		
		processor = kwargs.get('processor')
		if not processor:
			processor = lambda d: d
		
		serialiser = get_serialiser(format, request, processor, self.detail_level)
		mimetype = MIME_TYPES[format]
		
		if isinstance(data, Exception):
			data = serialiser.serialise(
				{
					'error': any(data.args) and data.args[0] or unicode(data)
				}
			)
			
			super(APIResponse, self).__init__(
				data, mimetype = mimetype
			)
			
			self.status_code = 400
			return
		
		if hasattr(data, '__iter__') and not isinstance(data, dict):
			page = request.GET.get('page', 1)
			rpp = request.GET.get('rpp', 100)
			
			try:
				rpp = int(rpp)
			except ValueError:
				return APIResponse(
					Exception('rpp not an integer')
				)
			
			paginator = Paginator(data, rpp)
			
			try:
				data = paginator.page(page)
			except EmptyPage:
				data = None
			except PageNotAnInteger:
				return APIResponse(
					Exception('page not an integer')
				)
			
			if data:
				data = data.object_list
		
		super(APIResponse, self).__init__(
			serialiser.serialise(data),
			mimetype = mimetype
		)