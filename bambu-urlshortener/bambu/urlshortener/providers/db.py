from django.contrib.sites.models import Site
from django.db import transaction
from bambu.urlshortener.providers import ProviderBase
from bambu.urlshortener.models import ShortURL

class DatabaseProvider(ProviderBase):
	def __init__(self):
		self.domain = Site.objects.get_current().domain
	
	def shorten(self, url):
		with transaction.commit_on_success():
			try:
				shortened = ShortURL.objects.get(url = url)
			except ShortURL.DoesNotExist:
				shortened = ShortURL.objects.create(url = url)
		
		return 'http://%s%s' % (self.domain, shortened.get_absolute_url())
	
	def unshorten(self, url):
		path = self.parse(url).path
		if path.startswith('/'):
			path = path[1:]
		
		if path.endswith('/'):
			path = path[:-1]
		
		return self.resolve(path)
	
	def resolve(self, slug):
		try:
			return ShortURL.objects.get(slug = slug).url
		except ShortURL.DoesNotExist:
			return None