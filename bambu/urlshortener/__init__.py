from django.conf import settings
from django.contrib.sites.models import Site

URL_LENGTH = getattr(settings, 'SHORTURL_LENGTH', 7)

def shorten(url):
	from bambu.urlshortener.models import ShortURL
	
	site = Site.objects.get_current()
	
	try:
		shortened = ShortURL.objects.filter(url = url).select_for_update(nowait = False)[0]
	except IndexError:
		shortened = ShortURL.objects.create(url = url)
	
	return 'http://%s%s' % (site.domain, shortened.get_absolute_url())