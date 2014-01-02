from django.conf.urls import patterns, url
from bambu.urlshortener import URL_LENGTH
from warnings import warn

warn('bambu.urlshortener.urls is deprecated. Use bambu.urlshortener.middleware.ShortURLFallbackMiddleware instead.', DeprecationWarning, stacklevel = 2)

urlpatterns = patterns('bambu.urlshortener.views',
	url(r'^(?P<slug>[a-zA-Z0-9]+)/$', 'url', name = 'short_url'),
)