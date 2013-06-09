from django.conf.urls import patterns, url
from bambu.urlshortener import URL_LENGTH

urlpatterns = patterns('bambu.urlshortener.views',
	url(r'^(?P<slug>[a-zA-Z0-9]+)/$', 'url', name = 'short_url'),
)