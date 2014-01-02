from urlparse import urlparse
from django.conf import settings
from django.contrib.sites.models import Site

class ProviderBase(object):
	def __init__(self):
		self.domain = getattr(settings, 'SHORTURL_DOMAIN', None)
	
	def shorten(self, url):
		return url
	
	def unshorten(self, url):
		return url
	
	def fix(self, url):
		if url.startswith('/'):
			return 'http://%s%s' % (Site.objects.get_current(), url)
		
		return url
	
	def resolve(self, slug):
		raise NotImplementedError('Method not implemented.')
	
	def parse(self, url):
		return urlparse(url)