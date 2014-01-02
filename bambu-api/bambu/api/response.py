from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models.query import QuerySet
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ImproperlyConfigured
from django.utils.http import urlencode
from bambu.api import serialisers
from bambu.api.exceptions import APIException

PAGE_LIMIT = getattr(settings, 'API_PAGE_LIMIT', None)

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
		
		headers = {}
		if hasattr(data, '__iter__') and not isinstance(data, dict):
			page = request.GET.get('page', 1)
			rpp = request.GET.get('rpp', PAGE_LIMIT)
			
			try:
				rpp = int(rpp)
			except ValueError:
				return APIResponse(
					Exception('rpp not an integer')
				)
			
			paginator = Paginator(data, rpp)
			
			try:
				page = paginator.page(page)
			except EmptyPage:
				super(APIResponse, self).__init__(
					serialiser.serialise(
						{
							'error': 'page argument empty'
						}
					),
					mimetype = mimetype
				)
				
				self.status_code = 400
				return
			except PageNotAnInteger:
				super(APIResponse, self).__init__(
					serialiser.serialise(
						{
							'error': 'page argument not an integer'
						}
					),
					mimetype = mimetype
				)
				
				self.status_code = 400
				return
			
			qs = request.GET.copy()
			qs['rpp'] = rpp
			
			if page.has_next():
				qs['page'] = page.number + 1
				headers['X-Page-Next'] = request.path + '?' + qs.urlencode()
			
			if page.has_previous():
				qs['page'] = page.number - 1
				headers['X-Page-Prev'] = request.path + '?' + qs.urlencode()
			
			if page:
				data = page.object_list
		
		try:
			content = serialiser.serialise(data)
		except APIException, ex:
			data = serialiser.serialise(
				{
					'error': any(ex.args) and ex.args[0] or unicode(ex)
				}
			)
			
			super(APIResponse, self).__init__(
				data, mimetype = mimetype
			)
			
			self.status_code = 400
			return
		
		super(APIResponse, self).__init__(
			content, mimetype = mimetype
		)
		
		for key, value in headers.items():
			self[key] = value