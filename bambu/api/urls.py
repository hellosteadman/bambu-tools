from django.conf.urls import patterns, include, url
from bambu import api

api.autodiscover()
urlpatterns = patterns('',
	url(r'^', include(api.site.urls))
)