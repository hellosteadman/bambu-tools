from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect

class DomainRedirectMiddleware(object):
	def __init__(self):
		self.domain = Site.objects.get_current().domain
	
	def process_request(self, request):
		domain = request.META.get('HTTP_HOST')
		if not domain or domain == 'localhost' or domain.startswith('localhost:'):
			return
		
		if self.domain != domain:
			path = request.path
			if request.META.get('QUERY_STRING'):
				path += '?' + request.META['QUERY_STRING']
			
			return HttpResponseRedirect(
				'http://%s%s' % (self.domain, path)
			)